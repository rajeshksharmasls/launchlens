from __future__ import annotations

from ..state import LaunchLensState


def fuse_research(state: LaunchLensState) -> LaunchLensState:
    demand = state.get("demand_data", {})
    supply = state.get("supply_data", {})
    demand_sources = demand.get("demand_sources", ["google_trends"])
    supply_sources = supply.get("supply_sources", ["amazon_search"])
    combined_message = (
        f"Demand signal from {', '.join(demand_sources)} is blended with supply signal from {', '.join(supply_sources)} "
        "to form a single launch verdict."
    )
    return {**state, "research_summary": combined_message}
