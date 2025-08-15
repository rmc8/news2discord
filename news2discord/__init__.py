import asyncio
import logging
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from logging import getLogger, StreamHandler, INFO
from typing import Any, Dict, List, Optional

import feedparser
import pandas as pd
from newspaper import Article
from tqdm import tqdm

from .flow import run as flow_run
from .models.config import ConfigModel, FeedConfigModel
from .models import OutputRecord, ArticleRecord
from .models.notification import NotificationModel
from .notification import discord

logger = getLogger(__name__)
logger.setLevel(INFO)

# ログハンドラーの設定
if not logger.handlers:
    handler = StreamHandler()
    handler.setLevel(INFO)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)


class News2Discord:
    USE_COL = ["title", "link", "published_jst", "site_name"]

    def __init__(self, config: ConfigModel, offset: int = 1):
        if not isinstance(offset, int):
            raise TypeError("Offset must be an integer")
        elif offset < 1:
            raise ValueError("Offset must be greater than or equal to 1")
        # init
        self.config = config
        self.feeds: List[FeedConfigModel] = config.get("feeds", [])
        self.notifications: Dict[str, Any] = config.get("notifications", {})
        self.offset: int = offset

        # 必須設定の検証
        if not self.feeds:
            raise ValueError("設定ファイルにfeedsが定義されていません")
        if not self.notifications.get("discord", {}).get("webhook_url"):
            raise ValueError("Discord webhook URLが設定されていません")

    @staticmethod
    def _parse_feed(feed: FeedConfigModel):
        parsed_feed = feedparser.parse(feed["url"])
        if parsed_feed.bozo:
            raise ValueError(f"Failed to parse feed: {feed['url']}")
        return parsed_feed

    @staticmethod
    def _conv_jst_time(df: pd.DataFrame):
        df["published"] = pd.to_datetime(df["published"], utc=True).dt.tz_convert(
            "Asia/Tokyo"
        )
        df["published_jst"] = df["published"]
        return df

    # ===== Time helpers =====
    @staticmethod
    def _now_jst() -> datetime:
        return datetime.now(tz=ZoneInfo("Asia/Tokyo"))

    def _compute_cutoff(self, run_time: Optional[datetime] = None) -> datetime:
        if run_time is None:
            run_time = self._now_jst()
        return run_time - timedelta(hours=self.offset)

    # ===== Feed utilities =====
    @staticmethod
    def _normalize_entries(
        entries: List[Dict[str, Any]], site_name: str
    ) -> pd.DataFrame:
        df = pd.json_normalize(entries)
        df["site_name"] = site_name
        return df

    def _filter_by_time(self, df: pd.DataFrame, cutoff: datetime) -> pd.DataFrame:
        return df[df["published_jst"].notna() & (df["published_jst"] >= cutoff)]

    # ===== Article utilities =====
    @staticmethod
    def _fetch_article(url: str, language: str = "ja") -> ArticleRecord:
        article = Article(url, language=language)
        article.download()
        article.parse()
        return {
            "title": article.title or "",
            "text": article.text or "",
            "html": article.article_html or "",
            "top_image": getattr(article, "top_image", ""),
        }

    def _build_output_record(self, base: Dict[str, Any]) -> Optional[OutputRecord]:
        url = base.get("link")
        if not url:
            return None
        try:
            art = self._fetch_article(url, language="ja")
        except Exception as e:
            logger.warning(f"Failed to fetch article: {url} ({type(e).__name__}: {e})")
            return None
        # Normalize and type-narrow fields for OutputRecord
        feed_title = str(base.get("title") or "")
        site_name = str(base.get("site_name") or "")
        published_raw = base.get("published_jst")
        if isinstance(published_raw, pd.Timestamp):
            published_jst = published_raw.to_pydatetime()
        elif isinstance(published_raw, datetime):
            published_jst = published_raw
        else:
            logger.warning(f"Invalid published_jst format: {type(published_raw)}")
            return None

        title_value = art["title"] or feed_title

        result: OutputRecord = {
            "title": title_value,
            "url": str(url),
            "site_name": site_name,
            "published_jst": published_jst,
            "text": art["text"],
            "html": art["html"],
            "top_image": art["top_image"],
            "text_length": len(art["text"]),
        }
        return result

    # ===== Main per-feed processing =====
    def _process_feed(
        self, feed: FeedConfigModel, run_time: Optional[datetime] = None
    ) -> List[OutputRecord]:
        parsed_feed = self._parse_feed(feed)
        site_name = feed["name"]
        entries = parsed_feed["entries"]
        df = self._normalize_entries(entries, site_name)
        df = self._conv_jst_time(df)
        udf = df[self.USE_COL]
        cutoff = self._compute_cutoff(run_time)
        fdf = self._filter_by_time(udf, cutoff)
        outputs: List[OutputRecord] = []
        for record in fdf.to_dict(orient="records"):
            out = self._build_output_record(record)
            if out is not None:
                outputs.append(out)
        return outputs

    async def _notify(self, notifications: list[NotificationModel]):
        # 設定からレート制限値を取得
        rate_limit_delay = self.config["notifications"]["discord"].get(
            "rate_limit_delay", 0.4
        )

        # レート制限を考慮して通知を送信
        for i, notification in enumerate(notifications):
            try:
                await discord.notification(notification, self.config)
                logger.info(
                    f"Sent notification {i + 1}/{len(notifications)}: {notification.title}"
                )

                # レート制限回避のため待機（最後の通知以外）
                if i < len(notifications) - 1:
                    await asyncio.sleep(rate_limit_delay)

            except Exception as e:
                logger.error(f"Failed to send notification {i + 1}: {e}")
                # エラーが発生しても続行
                continue

    async def run(self):
        fetched_feeds: list[OutputRecord] = []
        notifications: list[NotificationModel] = []
        run_time = self._now_jst()
        for feed in tqdm(self.feeds, desc="Processing feeds"):
            results = self._process_feed(feed, run_time)
            fetched_feeds.extend(results)
        for item in tqdm(fetched_feeds, desc="Processing articles"):
            # Replace with actual downstream processing (e.g., Discord notify)
            if item.get("text"):
                result = flow_run(item, self.config)
                if result.get("is_high_quality"):
                    notification = NotificationModel(
                        title=item["title"],
                        url=item["url"],
                        top_image=item["top_image"],
                        site_name=item["site_name"],
                        summary=result["summary"],
                        keywords=result["keywords"],
                    )
                    notifications.append(notification)
        # すべての通知を一括で処理
        if notifications:
            await self._notify(notifications)
