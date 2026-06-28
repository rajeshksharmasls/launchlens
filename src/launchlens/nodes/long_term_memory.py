from __future__ import annotations

from ..memory.long_term import extract_memory_facts, get_memory_store
from ..state import LaunchLensState


def recall_long_term_memory(state: LaunchLensState) -> LaunchLensState:
    thread_id = state.get("thread_id", "launchlens-default")
    user_input = state.get("user_input", "")
    records = get_memory_store().recall(thread_id, user_input)
    return {**state, "long_term_memory": [record.fact for record in records]}


def store_long_term_memory(state: LaunchLensState) -> LaunchLensState:
    thread_id = state.get("thread_id", "launchlens-default")
    facts = extract_memory_facts(
        user_input=state.get("user_input", ""),
        verdict=state.get("verdict", ""),
        region=state.get("region", "US"),
    )
    get_memory_store().remember(thread_id, facts)
    remembered = list(dict.fromkeys(list(state.get("long_term_memory", [])) + facts))
    return {**state, "long_term_memory": remembered}
