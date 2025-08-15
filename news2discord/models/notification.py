from pydantic import BaseModel


class NotificationModel(BaseModel):
    title: str
    site_name: str
    url: str
    top_image: str
    summary: str
    keywords: list[str]
