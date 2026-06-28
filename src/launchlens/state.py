from __future__ import annotations

from typing import Annotated, Any, TypedDict

from .reducers import merge_dicts


class LaunchLensState(TypedDict, total=False):
    user_input: str
    thread_id: str
    intent: str
    messages: list[str]
    summary: str
    long_term_memory: list[str]
    demand_data: Annotated[dict[str, Any], merge_dicts]
    supply_data: Annotated[dict[str, Any], merge_dicts]
    verdict: str
    region: str
    research_summary: str


def build_initial_state(user_input: str = "", region: str = "US") -> LaunchLensState:
    return {
        "user_input": user_input,
        "thread_id": "launchlens-default",
        "intent": "launch_review",
        "messages": [],
        "summary": "",
        "long_term_memory": [],
        "demand_data": {},
        "supply_data": {},
        "verdict": "",
        "region": region,
        "research_summary": "",
    }
