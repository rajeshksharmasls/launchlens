# Submission

## Project

LaunchLens is a LangGraph-based CLI agent that blends SerpApi demand signals and Oxylabs supply signals to deliver a Go / No-Go / Niche verdict for product ideas.

## What is included

- Runnable CLI chat loop
- Static browser UI with API integration and mock fallback
- Optional FastAPI adapter with health and chat endpoints
- LangGraph graph with routing, fan-out, tool-backed agent reasoning, short-term SQLite checkpointing, and long-term SQLite memory
- README with setup instructions, concept map, and demo prompts
- Architecture note and slide outline
- Environment template for required keys
- Mock-mode fixtures for SerpApi and Oxylabs-style research
- Tests for intent classification, summarization, research-plan construction, API service behavior, tool JSON, graph fan-out, and long-term memory

## Demo prompts

1. Should I launch a stainless-steel insulated water bottle in India under ₹1,500?
2. What about the US market?
3. Compare it to a cheaper bottle alternative.

## Suggested demo flow

1. Run `python main.py --cli` for the CLI demo, or open `ui/index.html` for the browser workbench.
2. Start with the India bottle launch question to show the full research path.
3. Ask the US follow-up to show conversational continuity.
4. Ask a pricing or review-gap question to show the routed fast branches.
5. Ask "What did you remember about the bottle?" to show long-term memory recall for the same thread.
6. Optionally run `uvicorn api.app:app --reload` after installing `.[api]` to connect the UI to the Python graph service.

## Notes

- Live API calls require SERPAPI_KEY and OXYLABS_API_KEY.
- Without keys, the app runs in mock mode using bundled fixtures.
- OPENAI_API_KEY is optional. Without it, LaunchLens still returns a deterministic verdict from the fused research signals.
- Long-term memory is stored in `long_term_memory.sqlite`, which is ignored by git.
