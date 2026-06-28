from __future__ import annotations

import os

from langchain.agents import create_agent
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from ..prompts import SYSTEM_PROMPT
from ..nodes.verdict import build_verdict
from ..state import LaunchLensState
from ..tools.oxylabs_tools import search_amazon_supply
from ..tools.serpapi_tools import search_google_shopping, search_google_trends


def run_agent(state: LaunchLensState) -> LaunchLensState:
    prompt = SYSTEM_PROMPT
    history = state.get("messages", [])
    long_term_memory = state.get("long_term_memory", [])
    formatted = build_verdict(state)
    if os.getenv("OPENAI_API_KEY"):
        try:
            llm = ChatOpenAI(model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"), temperature=0)
            agent = create_agent(
                llm,
                tools=[search_google_trends, search_google_shopping, search_amazon_supply],
                system_prompt=prompt,
            )
            response = agent.invoke(
                {
                    "messages": [
                        SystemMessage(content=prompt),
                        HumanMessage(
                            content=(
                                f"Long-term memory: {long_term_memory[:5]}\n"
                                f"Conversation history: {history[-4:]}\n"
                                f"Research summary: {formatted}"
                            )
                        ),
                    ]
                }
            )
            content = response["messages"][-1].content
            return {**state, "verdict": content}
        except Exception:
            pass

    return {**state, "verdict": formatted}
