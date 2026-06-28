from __future__ import annotations

from ..state import LaunchLensState


def build_verdict(state: LaunchLensState) -> str:
    demand = state.get("demand_data", {})
    supply = state.get("supply_data", {})
    demand_score = float(demand.get("demand_score", 5.0))
    supply_score = float(supply.get("supply_score", 5.0))
    price_band = supply.get("price_band", "₹700-₹1,500")
    related_queries = demand.get("related_queries", [])
    review_gaps = supply.get("review_gaps", [])
    headlines = demand.get("headlines", [])
    remembered = state.get("long_term_memory", [])
    combined_score = (demand_score + supply_score) / 2.0

    if combined_score >= 7.5:
        verdict = "Go"
        positioning = "Own a premium, problem-solving niche around thermal retention and giftability."
    elif combined_score >= 6.0:
        verdict = "Niche"
        positioning = "Target a focused segment that values durability and compact portability."
    else:
        verdict = "No-Go"
        positioning = "Delay the launch and revisit the category after clearer demand signals."

    lines = [
        f"Verdict: {verdict}",
        f"Demand: {demand.get('trend', 'mixed')} interest with related terms {', '.join(related_queries[:3]) or 'limited signals'}.",
        f"Price band: {price_band}.",
        f"Positioning: {positioning}",
        f"Review gaps: {', '.join(review_gaps[:3]) or 'No clear gaps identified'}.",
    ]

    if headlines:
        lines.append(f"Recent market signals: {', '.join(headlines[:2]) or 'no recent news signals'}.")

    lines.append(f"Memory: {'; '.join(remembered[:3]) if remembered else 'No durable product context recalled'}.")
    return "\n".join(lines)
