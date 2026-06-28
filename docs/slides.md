# LaunchLens presentation outline

## Slide 1 — Problem

- E-commerce founders often judge product ideas from scattered signals: search demand, marketplace saturation, prices, and review complaints.
- LaunchLens gives them a quick launch read before they spend on sourcing, branding, or ads.

## Slide 2 — Product

- CLI chat agent for product-launch viability.
- Input: a product idea and target market.
- Output: Go / No-Go / Niche verdict with demand, price band, positioning, and review-gap guidance.

## Slide 3 — Architecture

- LangGraph state machine captures the turn, routes intent, and preserves short-term plus long-term memory.
- Fan-out research runs SerpApi demand and Oxylabs-style supply lookups in parallel.
- Fusion and agent nodes synthesize the combined answer, with deterministic fixture fallback for demos.

## Slide 4 — Demo flow

- Ask: "Should I launch a stainless-steel insulated water bottle in India under ₹1,500?"
- Follow up: "What about the US market?" and "Compare it with a cheaper bottle alternative."
- Show that the agent keeps context, summarizes longer conversations, and recalls durable product facts.

## Slide 5 — Why it matters

- Reduces early launch risk by combining demand and competition signals.
- Converts raw marketplace research into founder-friendly action.
- Works in mock mode for reliable demos, can switch to live APIs when keys are present, and remembers durable product context by thread.

## Slide 6 — Next steps

- Add richer scoring calibration by category and region.
- Store historical launch briefs for side-by-side comparison.
- Expand the UI beyond CLI into a lightweight founder dashboard.
