from typing_extensions import Any

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from ..models.flow import State, JudgeModel


def judge(state: State) -> dict[str, Any]:
    llm = ChatOpenAI(
        model=state["config"]["ai"]["judge"]["model"],
        temperature=state["config"]["ai"]["judge"]["temperature"],
    )
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", state["config"]["ai"]["judge"]["system_prompt"]),
            ("user", "要約の内容: {summary}"),
        ]
    )
    chain = prompt | llm.with_structured_output(JudgeModel)
    result = chain.invoke({"summary": state["summary"]})
    return {
        "is_high_quality": result.is_high_quality,
    }
