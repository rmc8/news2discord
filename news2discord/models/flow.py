from typing_extensions import TypedDict

from pydantic import BaseModel, Field

from ..models.config import ConfigModel


class State(TypedDict):
    text: str
    url: str
    summary: str
    keywords: list[str]
    is_high_quality: bool
    config: ConfigModel


class SummaryModel(BaseModel):
    summary: str = Field(..., description="記事の要約を格納する")
    keywords: list[str] = Field(
        ...,
        description="記事のキーワードを最大で5つ格納する",
        max_length=5,
        min_length=1,
    )


class JudgeModel(BaseModel):
    is_high_quality: bool = Field(
        ...,
        description="要約した記事をユーザーに送信すべきであるか品質を判定する。送信しても良い品質であればTrueとして送信すべきでなければFalseとする。",
    )
