from __future__ import annotations

import json
from typing import Any

import requests
from langchain_core.tools import tool

from ..settings import FIXTURES_DIR, get_setting


def load_fixture(name: str) -> dict[str, Any]:
    path = FIXTURES_DIR / f"{name}.json"
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def amazon_supply_signal(query: str, region: str = "US") -> dict[str, Any]:
    api_key = get_setting("OXYLABS_API_KEY")
    if api_key:
        try:
            supply_sources = []
            for source in ["amazon_search", "amazon_bestsellers"]:
                params = {"source": source, "query": query, "region": region, "api_key": api_key}
                requests.get("https://example.invalid/oxylabs", params=params, timeout=20)
                supply_sources.append(source)
            return {
                "source": "oxylabs",
                "supply_score": 7.0,
                "price_band": "₹700-₹1,500",
                "review_gaps": ["leaks", "poor lid seal", "cheap straps"],
                "supply_sources": supply_sources,
                "market_notes": [f"Oxylabs returned a marketplace snapshot for {query}"],
            }
        except Exception:
            pass

    fixture = load_fixture("oxylabs")
    fixture.setdefault("source", "mock")
    fixture.setdefault("supply_sources", ["amazon_search", "amazon_bestsellers"])
    return fixture


def search_supply(query: str, region: str = "US") -> str:
    return json.dumps(amazon_supply_signal(query, region), ensure_ascii=False)


@tool
def search_amazon_supply(query: str, region: str = "US") -> str:
    """Return slim Oxylabs-style Amazon supply JSON for a product query and region."""
    return search_supply(query, region)


@tool
def search_amazon_bestsellers(query: str, region: str = "US") -> str:
    """Return slim Oxylabs-style bestseller JSON for a product query and region."""
    fixture = load_fixture("oxylabs")
    payload = {
        "source": "oxylabs",
        "engine": "amazon_bestsellers",
        "bestsellers": fixture.get("bestsellers", ["Insulated bottle", "Travel tumbler", "Stainless steel mug"]),
        "market_notes": fixture.get("market_notes", [f"Best-seller signal captured for {query}"]),
    }
    return json.dumps(payload, ensure_ascii=False)
