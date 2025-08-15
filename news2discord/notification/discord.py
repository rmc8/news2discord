import aiohttp
import discord
import asyncio
from logging import getLogger

from ..models.config import ConfigModel
from ..models.notification import NotificationModel

logger = getLogger(__name__)
logger.setLevel("INFO")

COLOR_MAP = {"ACCENT": 0x009999}

# レート制限設定
RATE_LIMIT_DELAY = 0.4  # 秒
MAX_RETRIES = 3
RETRY_DELAY = 1.0  # 秒


async def notification(notification: NotificationModel, config: ConfigModel) -> None:
    webhook_url = config["notifications"]["discord"]["webhook_url"]
    if not webhook_url:
        logger.error("Discord webhook URL is not configured")
        return

    for attempt in range(MAX_RETRIES):
        try:
            async with aiohttp.ClientSession() as session:
                webhook = discord.Webhook.from_url(webhook_url, session=session)
                embed = discord.Embed(
                    title=notification.title,
                    url=notification.url,
                    description=notification.summary,
                    color=COLOR_MAP["ACCENT"],
                )
                embed.set_author(name=notification.site_name)
                embed.add_field(
                    name="キーワード", value=", ".join(notification.keywords)
                )
                image_url = notification.top_image
                if image_url and image_url.startswith("http"):
                    embed.set_image(url=image_url)

                await webhook.send(embed=embed)
                logger.info(f"Successfully sent notification: {notification.title}")
                return  # 成功したら終了

        except discord.HTTPException as e:
            if e.status == 429:  # Rate limited
                retry_after = (
                    e.retry_after if hasattr(e, "retry_after") else RETRY_DELAY
                )
                logger.warning(
                    f"Rate limited, retrying in {retry_after}s (attempt {attempt + 1}/{MAX_RETRIES})"
                )
                await asyncio.sleep(retry_after)
            else:
                logger.error(f"Discord API error (HTTP {e.status}): {e}")
                break
        except aiohttp.ClientError as e:
            logger.error(f"Network error while sending notification: {e}")
            if attempt < MAX_RETRIES - 1:
                await asyncio.sleep(RETRY_DELAY)
        except Exception as e:
            logger.error(f"Unexpected error while sending notification: {e}")
            break

    logger.error(
        f"Failed to send notification after {MAX_RETRIES} attempts: {notification.title}"
    )
