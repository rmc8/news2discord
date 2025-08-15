from typing import cast

from langgraph.graph import StateGraph, START, END

from ..models.config import ConfigModel
from ..models.record import OutputRecord
from ..models.flow import State
from .summarize import summarize
from .judge import judge


def _create_graph():
    graph = StateGraph(State)
    graph.add_node("summarize", summarize)
    graph.add_node("judge", judge)
    graph.add_edge(START, "summarize")
    graph.add_edge("summarize", "judge")
    graph.add_edge("judge", END)
    return graph


def run(feed: OutputRecord, config: ConfigModel) -> State:
    graph = _create_graph()
    app = graph.compile()
    state: State = cast(
        State,
        {
            "text": feed["text"],
            "url": feed["url"],
            "summary": "",
            "keywords": [],
            "is_high_quality": False,
            "config": config,
        },
    )
    result = app.invoke(state)
    return result
