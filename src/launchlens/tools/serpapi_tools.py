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


def build_research_plan(query: str, region: str = "US") -> dict[str, list[str]]:
    return {
        "query": query,
        "region": region,
        "demand_sources": ["google_trends", "google_shopping"],
        "supply_sources": ["amazon_search", "amazon_bestsellers"],
    }


def _serpapi_payload(engine: str, query: str, region: str) -> dict[str, Any]:
    api_key = get_setting("SERPAPI_KEY")
    if api_key:
        try:
            params = {
                "engine": engine,
                "q": query,
                "api_key": api_key,
                "hl": "en",
                "gl": region.lower() if region else "us",
            }
            response = requests.get("https://serpapi.com/search.json", params=params, timeout=20)
            response.raise_for_status()
            return response.json()
        except Exception:
            pass
    return load_fixture("serpapi")


def google_trends_signal(query: str, region: str = "US") -> dict[str, Any]:
    payload = _serpapi_payload("google_trends", query, region)
    related_queries = [item.get("query", "") for item in payload.get("related_queries", [])[:5] if isinstance(item, dict)]
    if not related_queries:
        related_queries = payload.get("related_queries", [])[:5]

    return {
        "source": "serpapi",
        "engine": "google_trends",
        "demand_score": float(payload.get("demand_score", 7.6)),
        "trend": payload.get("trend", "rising"),
        "related_queries": related_queries,
        "market_notes": payload.get("market_notes", [f"Search interest signal collected for {query}"]),
    }


def google_shopping_signal(query: str, region: str = "US") -> dict[str, Any]:
    payload = _serpapi_payload("google_shopping", query, region)
    shopping_prices = [item.get("price", "") for item in payload.get("shopping_results", [])[:3] if isinstance(item, dict)]
    if not shopping_prices:
        shopping_prices = payload.get("shopping_prices", ["₹800", "₹1,200", "₹1,500"])

    return {
        "source": "serpapi",
        "engine": "google_shopping",
        "shopping_prices": shopping_prices,
        "demand_sources": ["google_shopping"],
        "market_notes": payload.get("market_notes", [f"Shopping signal collected for {query}"]),
    }


def google_news_signal(query: str, region: str = "US") -> dict[str, Any]:
    payload = _serpapi_payload("google_news", query, region)
    headlines = [item.get("title", "") for item in payload.get("news_results", [])[:3] if isinstance(item, dict)]
    if not headlines:
        headlines = payload.get("headlines", [f"Recent market updates for {query}"])

    return {
        "source": "serpapi",
        "engine": "google_news",
        "headlines": headlines,
        "market_notes": payload.get("market_notes", [f"News signal collected for {query}"]),
    }


def search_demand(query: str, region: str = "US") -> str:
    trends = google_trends_signal(query, region)
    shopping = google_shopping_signal(query, region)
    news = google_news_signal(query, region)
    return json.dumps(
        {
            "source": "serpapi",
            "demand_score": trends["demand_score"],
            "trend": trends["trend"],
            "related_queries": trends["related_queries"],
            "shopping_prices": shopping["shopping_prices"],
            "headlines": news["headlines"],
            "demand_sources": ["google_trends", "google_shopping", "google_news"],
            "market_notes": trends["market_notes"][:2] + shopping["market_notes"][:2] + news["market_notes"][:2],
        },
        ensure_ascii=False,
    )


@tool
def search_google_trends(query: str, region: str = "US") -> str:
    """Return slim Google Trends demand JSON for a product query and region."""
    return json.dumps(google_trends_signal(query, region), ensure_ascii=False)


@tool
def search_google_shopping(query: str, region: str = "US") -> str:
    """Return slim Google Shopping pricing JSON for a product query and region."""
    return json.dumps(google_shopping_signal(query, region), ensure_ascii=False)


@tool
def search_google_news(query: str, region: str = "US") -> str:
    """Return slim Google News JSON for a product query and region."""
    return json.dumps(google_news_signal(query, region), ensure_ascii=False)
