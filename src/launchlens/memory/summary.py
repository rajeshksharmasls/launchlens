from __future__ import annotations

from ..nodes.summarizer import summarize_messages


def summarize_thread(messages: list[str]) -> str:
    return summarize_messages(messages)
