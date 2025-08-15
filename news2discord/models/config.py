from typing_extensions import TypedDict

# AI


class SummarizationConfigModel(TypedDict):
    model: str
    temperature: float
    system_prompt: str


class JudgeConfigModel(TypedDict):
    model: str
    temperature: float
    system_prompt: str


class AiConfigModel(TypedDict):
    summarization: SummarizationConfigModel
    judge: JudgeConfigModel


# Notification


class DiscordConfigModel(TypedDict):
    webhook_url: str
    rate_limit_delay: float  # 通知間の待機時間（秒）
    max_retries: int  # 最大リトライ回数


class NotificationConfigModel(TypedDict):
    discord: DiscordConfigModel


# Feed
class FeedConfigModel(TypedDict):
    name: str
    url: str


# General
class ConfigModel(TypedDict):
    ai: AiConfigModel
    notifications: NotificationConfigModel
    feeds: list[FeedConfigModel]
