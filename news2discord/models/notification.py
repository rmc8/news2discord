from pydantic import BaseModel

from .config import ConfigModel


class NotificationModel(BaseModel):
    title: str
    site_name: str
    url: str
    eyecatch: str
    summary: str
    keywords: list[str]
