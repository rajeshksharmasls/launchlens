from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from uuid import uuid4

from src.launchlens.graph import build_graph
from src.launchlens.state import LaunchLensState, build_initial_state


@dataclass(frozen=True)
class ChatRequest:
    message: str
    region: str = "US"
    thread_id: str | None = None


class LaunchLensService:
    def __init__(self) -> None:
        self._graph = build_graph()
        self._thread_states: dict[str, LaunchLensState] = {}

    def health(self) -> dict[str, str]:
        return {"status": "ok", "service": "LaunchLens"}

    def chat(self, request: ChatRequest) -> dict[str, Any]:
        message = request.message.strip()
        if not message:
            raise ValueError("message is required")

        thread_id = request.thread_id or f"launchlens-api-{uuid4()}"
        state = self._thread_states.get(thread_id, build_initial_state(region=request.region))
        state = {**state, "user_input": message, "region": request.region, "thread_id": thread_id}
        result = self._graph.invoke(state, config={"configurable": {"thread_id": thread_id}})
        self._thread_states[thread_id] = result

        return {
            "thread_id": thread_id,
            "region": result.get("region", request.region),
            "intent": result.get("intent", ""),
            "verdict": result.get("verdict", ""),
            "research_summary": result.get("research_summary", ""),
            "long_term_memory": result.get("long_term_memory", []),
        }


def create_service() -> LaunchLensService:
    return LaunchLensService()


def create_app():
    service = create_service()

    try:
        from fastapi import FastAPI, HTTPException
        from fastapi.middleware.cors import CORSMiddleware
        from pydantic import BaseModel
    except ImportError:
        return service

    class ChatPayload(BaseModel):
        message: str
        region: str = "US"
        thread_id: str | None = None

    app = FastAPI(title="LaunchLens API", version="0.1.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["*"],
    )

    @app.get("/health")
    def health() -> dict[str, str]:
        return service.health()

    @app.post("/chat")
    def chat(payload: ChatPayload) -> dict[str, Any]:
        try:
            return service.chat(
                ChatRequest(
                    message=payload.message,
                    region=payload.region,
                    thread_id=payload.thread_id,
                )
            )
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    return app


app = create_app()
