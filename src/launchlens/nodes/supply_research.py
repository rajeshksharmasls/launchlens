from __future__ import annotations

import json

from ..state import LaunchLensState
from ..tools.oxylabs_tools import search_supply


def supply_research(state: LaunchLensState) -> LaunchLensState:
    user_input = state.get("user_input", "")
    region = state.get("region", "US")
    supply_payload = json.loads(search_supply(user_input, region))
    return {**state, "supply_data": supply_payload}
