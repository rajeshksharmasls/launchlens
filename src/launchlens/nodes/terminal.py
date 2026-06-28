from __future__ import annotations

from ..state import LaunchLensState


def capture_user_message(state: LaunchLensState) -> LaunchLensState:
    user_input = state.get("user_input", "")
    messages = list(state.get("messages", []))
    if user_input:
        messages.append(f"User: {user_input}")
    return {**state, "messages": messages}


def append_assistant_message(state: LaunchLensState) -> LaunchLensState:
    verdict = state.get("verdict", "")
    messages = list(state.get("messages", []))
    if verdict:
        messages.append(f"Assistant: {verdict}")
    return {**state, "messages": messages}
