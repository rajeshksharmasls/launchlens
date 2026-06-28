from __future__ import annotations

import sys

from langgraph.graph import END, START, StateGraph

from .agents.market_agent import run_agent
from .memory.checkpoint import get_checkpointer
from .nodes.fusion import fuse_research
from .nodes.long_term_memory import recall_long_term_memory, store_long_term_memory
from .nodes.router import route_request, route_to_next
from .nodes.summarizer import summarize_history
from .nodes.terminal import append_assistant_message, capture_user_message
from .state import LaunchLensState, build_initial_state
from .tools.oxylabs_tools import amazon_supply_signal
from .tools.serpapi_tools import google_shopping_signal, google_trends_signal


def google_trends_research(state: LaunchLensState) -> LaunchLensState:
    trends = google_trends_signal(state.get("user_input", ""), state.get("region", "US"))
    return {
        "demand_data": {
            "source": "serpapi",
            "demand_score": trends.get("demand_score", 7.6),
            "trend": trends.get("trend", "rising"),
            "related_queries": trends.get("related_queries", []),
            "demand_sources": ["google_trends"],
            "market_notes": trends.get("market_notes", [])[:2],
        }
    }


def google_shopping_research(state: LaunchLensState) -> LaunchLensState:
    shopping = google_shopping_signal(state.get("user_input", ""), state.get("region", "US"))
    return {
        "demand_data": {
            "shopping_prices": shopping.get("shopping_prices", []),
            "demand_sources": ["google_trends", "google_shopping"],
            "market_notes": shopping.get("market_notes", [])[:2],
        }
    }


def amazon_supply_research(state: LaunchLensState) -> LaunchLensState:
    amazon = amazon_supply_signal(state.get("user_input", ""), state.get("region", "US"))
    return {"supply_data": amazon}


def pricing_analysis(state: LaunchLensState) -> LaunchLensState:
    supply = state.get("supply_data", {})
    price_band = supply.get("price_band", "₹700-₹1,500")
    return {
        **state,
        "verdict": f"Pricing readout: the current market band is {price_band}; the opportunity is strongest when the founder targets a value-led premium position.",
    }


def review_gap_analysis(state: LaunchLensState) -> LaunchLensState:
    supply = state.get("supply_data", {})
    review_gaps = supply.get("review_gaps", ["leaks", "poor lid seal"])
    return {
        **state,
        "verdict": f"Review-gap readout: recurring complaints suggest product opportunities around {', '.join(review_gaps[:3])}.",
    }


def build_graph():
    builder = StateGraph(LaunchLensState)
    builder.add_node("capture_user_message", capture_user_message)
    builder.add_node("recall_long_term_memory", recall_long_term_memory)
    builder.add_node("route_request", route_request)
    builder.add_node("summarize_history", summarize_history)
    builder.add_node("google_trends_research", google_trends_research)
    builder.add_node("google_shopping_research", google_shopping_research)
    builder.add_node("amazon_supply_research", amazon_supply_research)
    builder.add_node("fuse_research", fuse_research)
    builder.add_node("pricing_analysis", pricing_analysis)
    builder.add_node("review_gap_analysis", review_gap_analysis)
    builder.add_node("agent_node", run_agent)
    builder.add_node("append_assistant_message", append_assistant_message)
    builder.add_node("store_long_term_memory", store_long_term_memory)

    builder.add_edge(START, "capture_user_message")
    builder.add_edge("capture_user_message", "recall_long_term_memory")
    builder.add_edge("recall_long_term_memory", "route_request")
    builder.add_conditional_edges(
        "route_request",
        route_to_next,
        {
            "summarize_history": "summarize_history",
            "pricing_analysis": "pricing_analysis",
            "review_gap_analysis": "review_gap_analysis",
            "google_trends_research": "google_trends_research",
            "google_shopping_research": "google_shopping_research",
            "amazon_supply_research": "amazon_supply_research",
        },
    )
    builder.add_edge("summarize_history", "google_trends_research")
    builder.add_edge("summarize_history", "google_shopping_research")
    builder.add_edge("summarize_history", "amazon_supply_research")
    builder.add_edge("google_trends_research", "fuse_research")
    builder.add_edge("google_shopping_research", "fuse_research")
    builder.add_edge("amazon_supply_research", "fuse_research")
    builder.add_edge("fuse_research", "agent_node")
    builder.add_edge("pricing_analysis", "append_assistant_message")
    builder.add_edge("review_gap_analysis", "append_assistant_message")
    builder.add_edge("agent_node", "append_assistant_message")
    builder.add_edge("append_assistant_message", "store_long_term_memory")
    builder.add_edge("store_long_term_memory", END)

    checkpointer = get_checkpointer()
    if checkpointer is not None:
        return builder.compile(checkpointer=checkpointer)
    return builder.compile()


def run_cli() -> None:
    graph = build_graph()
    print("LaunchLens ready. Type a product idea or 'exit' to quit.")
    thread_id = "launchlens-default"
    state = {**build_initial_state(""), "thread_id": thread_id}

    while True:
        try:
            user_input = input("Founder> ").strip()
        except EOFError:
            break
        if not user_input:
            continue
        if user_input.lower() in {"exit", "quit"}:
            print("Goodbye.")
            break

        config = {"configurable": {"thread_id": thread_id}}
        state = {**state, "user_input": user_input, "thread_id": thread_id}
        result = graph.invoke(state, config=config)
        state = result
        print(result.get("verdict", "No verdict produced."))
        print()


def main() -> None:
    if len(sys.argv) > 1 and sys.argv[1] in {"--cli", "cli"}:
        run_cli()
        return
    print("LaunchLens CLI ready. Run 'python main.py --cli' to start the chat loop.")
