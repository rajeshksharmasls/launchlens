from __future__ import annotations

import json

from ..state import LaunchLensState
from ..tools.serpapi_tools import build_research_plan, search_demand


def demand_research(state: LaunchLensState) -> LaunchLensState:
    user_input = state.get("user_input", "")
    region = state.get("region", "US")
    plan = build_research_plan(user_input, region)
    demand_payload = json.loads(search_demand(user_input, region))
    return {
        **state,
        "demand_data": demand_payload,
        "research_summary": f"Research plan: demand sources {', '.join(plan['demand_sources'])}; supply sources {', '.join(plan['supply_sources'])}",
    }
