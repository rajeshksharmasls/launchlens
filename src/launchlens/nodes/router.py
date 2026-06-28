from __future__ import annotations

from ..state import LaunchLensState


def classify_intent(user_input: str) -> str:
    text = user_input.lower()
    if any(token in text for token in ["price", "pricing", "cost", "budget", "cheap", "expensive"]):
        return "pricing_question"
    if any(token in text for token in ["review", "complaint", "pain point", "gap", "problem"]):
        return "review_gap"
    if any(token in text for token in ["launch", "worth it", "go/no-go", "go no go", "position", "niche", "should i", "is it worth"]):
        return "launch_review"
    if any(token in text for token in ["what about", "compare", "how about", "also", "instead", "similar", "cheaper", "more expensive", "us market", "india market"]):
        return "follow_up"
    return "general_chat"


def route_request(state: LaunchLensState) -> LaunchLensState:
    user_input = state.get("user_input", "")
    return {**state, "intent": classify_intent(user_input)}


def route_to_next(state: LaunchLensState) -> str | list[str]:
    intent = state.get("intent", "launch_review")
    if len(state.get("messages", [])) >= 6:
        return "summarize_history"
    if intent == "pricing_question":
        return "pricing_analysis"
    if intent == "review_gap":
        return "review_gap_analysis"
    return ["google_trends_research", "google_shopping_research", "amazon_supply_research"]
