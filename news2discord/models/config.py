from typing_extensions import TypedDict

# AI


class SummarizationConfigModel(TypedDict):
    model: str
    temperature: float
    system_prompt: str


class AiConfigModel(TypedDict):
    summarization: SummarizationConfigModel


# Notification


class DiscordConfigModel(TypedDict):
    webhook_url: str


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
