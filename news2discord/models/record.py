from datetime import datetime
from typing_extensions import TypedDict


class ArticleRecord(TypedDict):
    title: str
    text: str
    html: str
    top_image: str


class OutputRecord(TypedDict):
    title: str
    url: str
    site_name: str
    published_jst: datetime
    text: str
    html: str
    top_image: str
    text_length: int
