from typing_extensions import Any

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from ..models.flow import State, SummaryModel


def summarize(state: State) -> dict[str, Any]:
    llm = ChatOpenAI(
        model=state["config"]["ai"]["summarization"]["model"],
        temperature=state["config"]["ai"]["summarization"]["temperature"],
    )
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", state["config"]["ai"]["summarization"]["system_prompt"]),
            ("user", "記事の内容: {text}"),
        ]
    )
    chain = prompt | llm.with_structured_output(SummaryModel)
    result = chain.invoke({"text": state["text"]})
    return {
        "summary": result.summary,
        "keywords": result.keywords,
    }
