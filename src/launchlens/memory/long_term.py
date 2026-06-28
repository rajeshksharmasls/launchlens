from __future__ import annotations

import re
import sqlite3
from contextlib import closing
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from ..settings import PROJECT_ROOT


DEFAULT_MEMORY_PATH = PROJECT_ROOT / "long_term_memory.sqlite"


@dataclass(frozen=True)
class MemoryRecord:
    namespace: str
    fact: str
    created_at: str


class LongTermMemoryStore:
    def __init__(self, path: Path = DEFAULT_MEMORY_PATH) -> None:
        self.path = path
        self._ensure_schema()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.path)

    def _ensure_schema(self) -> None:
        with closing(self._connect()) as conn:
            with conn:
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS memories (
                        namespace TEXT NOT NULL,
                        fact TEXT NOT NULL,
                        created_at TEXT NOT NULL,
                        PRIMARY KEY (namespace, fact)
                    )
                    """
                )

    def remember(self, namespace: str, facts: list[str]) -> None:
        if not facts:
            return

        now = datetime.now(UTC).isoformat()
        rows = [(namespace, fact, now) for fact in dict.fromkeys(facts) if fact]
        with closing(self._connect()) as conn:
            with conn:
                conn.executemany(
                    "INSERT OR IGNORE INTO memories(namespace, fact, created_at) VALUES (?, ?, ?)",
                    rows,
                )

    def recall(self, namespace: str, query: str, limit: int = 5) -> list[MemoryRecord]:
        with closing(self._connect()) as conn:
            rows = conn.execute(
                """
                SELECT namespace, fact, created_at
                FROM memories
                WHERE namespace = ?
                ORDER BY created_at DESC
                """,
                (namespace,),
            ).fetchall()

        records = [MemoryRecord(namespace=row[0], fact=row[1], created_at=row[2]) for row in rows]
        ranked = sorted(records, key=lambda record: _score_fact(record.fact, query), reverse=True)
        return ranked[:limit]


def get_memory_store() -> LongTermMemoryStore:
    return LongTermMemoryStore()


def extract_memory_facts(user_input: str, verdict: str, region: str) -> list[str]:
    facts: list[str] = []
    text = user_input.strip()
    if not text:
        return facts

    product_match = re.search(
        r"(?:launch|sell|build|compare)\s+(?:a|an|the)?\s*([^?]{3,80}?)(?:\s+in\s+|\s+under\s+|\?|$)",
        text,
        flags=re.IGNORECASE,
    )
    if product_match:
        facts.append(f"Product idea: {product_match.group(1).strip()}")

    price_match = re.search(r"(?:under|below|budget(?: of)?|price(?:d)? at)\s+([^\s?]+)", text, flags=re.IGNORECASE)
    if price_match:
        facts.append(f"Price constraint: {price_match.group(1).strip()}")

    if region:
        facts.append(f"Preferred region: {region.upper()}")

    verdict_line = next((line.strip() for line in verdict.splitlines() if line.lower().startswith("verdict:")), "")
    if verdict_line:
        facts.append(f"Prior launch decision: {verdict_line}")

    return facts


def _score_fact(fact: str, query: str) -> int:
    query_terms = {term for term in re.findall(r"[a-z0-9]+", query.lower()) if len(term) > 2}
    fact_terms = set(re.findall(r"[a-z0-9]+", fact.lower()))
    return len(query_terms & fact_terms)
