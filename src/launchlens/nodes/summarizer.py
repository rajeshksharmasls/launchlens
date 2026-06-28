from __future__ import annotations

import re

from ..state import LaunchLensState


def summarize_messages(messages: list[str]) -> str:
    if not messages:
        return "No prior conversation yet."

    joined = " ".join(messages[-6:]).lower()
    topic = "the product"
    product_match = re.search(r"launching a ([a-z0-9 -]+)", joined)
    if product_match:
        topic = product_match.group(1).strip()
    elif "india" in joined:
        topic = "the India market"
    elif "us" in joined:
        topic = "the US market"

    if "price" in joined or "pricing" in joined:
        focus = "pricing"
    elif "review" in joined or "complaint" in joined:
        focus = "customer feedback"
    else:
        focus = "launch viability"

    return (
        f"Summary: the conversation covered {topic} with emphasis on {focus}; "
        "the latest turns focused on demand, market fit, and positioning."
    )


def summarize_history(state: LaunchLensState) -> LaunchLensState:
    messages = list(state.get("messages", []))
    summary = summarize_messages(messages)
    condensed = messages[-4:]
    condensed.append(f"Summary: {summary}")
    return {**state, "summary": summary, "messages": condensed}
