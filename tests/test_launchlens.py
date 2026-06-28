import unittest
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from api.app import ChatRequest, LaunchLensService
from main import build_research_plan, classify_intent, summarize_messages
from src.launchlens.memory.long_term import LongTermMemoryStore, extract_memory_facts
from src.launchlens.nodes.router import route_to_next
from src.launchlens.tools.oxylabs_tools import search_amazon_bestsellers, search_amazon_supply
from src.launchlens.tools.serpapi_tools import search_google_news, search_google_trends


class LaunchLensTests(unittest.TestCase):
    def test_classify_intent_for_launch_questions(self):
        intent = classify_intent("Should I launch a stainless steel bottle in India?")
        self.assertEqual(intent, "launch_review")

    def test_classify_intent_for_follow_up(self):
        intent = classify_intent("What about the US market?")
        self.assertEqual(intent, "follow_up")

    def test_summarize_messages_compacts_history(self):
        messages = [
            "User: I am thinking of launching a blender in India",
            "Assistant: Demand looks moderate but there is room for premium positioning",
            "User: What about the US market?",
            "Assistant: The US is more crowded but pricing could be higher",
            "User: Can you compare it with a cheaper alternative?",
            "Assistant: The cheaper alternative is less differentiated",
        ]
        summary = summarize_messages(messages)
        self.assertIn("blender", summary.lower())
        self.assertIn("us", summary.lower())

    def test_build_research_plan_uses_multiple_sources(self):
        plan = build_research_plan("insulated bottle", "IN")
        self.assertGreaterEqual(len(plan["demand_sources"]), 2)
        self.assertGreaterEqual(len(plan["supply_sources"]), 2)

    def test_router_fans_out_full_research(self):
        next_nodes = route_to_next({"intent": "launch_review", "messages": []})
        self.assertEqual(
            next_nodes,
            ["google_trends_research", "google_shopping_research", "amazon_supply_research"],
        )

    @patch.dict("os.environ", {"SERPAPI_KEY": "", "OXYLABS_API_KEY": ""})
    def test_tools_return_slim_json(self):
        trends = json.loads(search_google_trends.invoke({"query": "insulated bottle", "region": "IN"}))
        news = json.loads(search_google_news.invoke({"query": "insulated bottle", "region": "IN"}))
        amazon = json.loads(search_amazon_supply.invoke({"query": "insulated bottle", "region": "IN"}))
        bestselling = json.loads(search_amazon_bestsellers.invoke({"query": "insulated bottle", "region": "IN"}))
        self.assertIn("demand_score", trends)
        self.assertIn("headlines", news)
        self.assertIn("review_gaps", amazon)
        self.assertIn("bestsellers", bestselling)
        self.assertNotIn("html", trends)
        self.assertNotIn("html", news)
        self.assertNotIn("html", amazon)
        self.assertNotIn("html", bestselling)

    def test_long_term_memory_store_persists_and_recalls(self):
        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "memory.sqlite"
            store = LongTermMemoryStore(path)
            store.remember("founder-1", ["Product idea: insulated bottle", "Preferred region: IN"])
            records = store.recall("founder-1", "bottle India")
            self.assertEqual(records[0].fact, "Product idea: insulated bottle")

            reloaded = LongTermMemoryStore(path)
            reloaded_records = reloaded.recall("founder-1", "region")
            self.assertTrue(any(record.fact == "Preferred region: IN" for record in reloaded_records))

    def test_extract_memory_facts_keeps_product_price_and_verdict(self):
        facts = extract_memory_facts(
            "Should I launch a stainless steel bottle in India under ₹1,500?",
            "Verdict: Niche\nDemand: rising.",
            "IN",
        )
        self.assertTrue(any(fact.startswith("Product idea:") for fact in facts))
        self.assertIn("Price constraint: ₹1,500", facts)
        self.assertIn("Prior launch decision: Verdict: Niche", facts)

    @patch.dict("os.environ", {"SERPAPI_KEY": "", "OXYLABS_API_KEY": "", "OPENAI_API_KEY": ""})
    def test_api_service_returns_chat_response(self):
        service = LaunchLensService()
        response = service.chat(ChatRequest(message="Should I launch a bottle in India?", region="IN"))
        self.assertEqual(response["intent"], "launch_review")
        self.assertIn("Verdict:", response["verdict"])
        self.assertTrue(response["thread_id"].startswith("launchlens-api-"))

    @patch.dict("os.environ", {"SERPAPI_KEY": "", "OXYLABS_API_KEY": "", "OPENAI_API_KEY": ""})
    def test_api_service_reuses_thread_state(self):
        service = LaunchLensService()
        first = service.chat(ChatRequest(message="Should I launch a bottle in India?", region="IN", thread_id="test-thread"))
        second = service.chat(ChatRequest(message="What about the US market?", region="US", thread_id="test-thread"))
        self.assertEqual(first["thread_id"], second["thread_id"])
        self.assertEqual(second["intent"], "follow_up")

    @patch.dict("os.environ", {"SERPAPI_KEY": "", "OXYLABS_API_KEY": "", "OPENAI_API_KEY": ""})
    def test_api_service_returns_long_term_memory(self):
        service = LaunchLensService()
        service.chat(
            ChatRequest(
                message="Should I launch a stainless steel bottle in India under \u20b91,500?",
                region="IN",
                thread_id="memory-test-thread",
            )
        )
        response = service.chat(
            ChatRequest(
                message="What did you remember about the bottle?",
                region="IN",
                thread_id="memory-test-thread",
            )
        )
        self.assertTrue(any("Product idea:" in fact for fact in response["long_term_memory"]))
