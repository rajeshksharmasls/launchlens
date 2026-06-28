from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ResearchBundle:
    demand: dict[str, Any] = field(default_factory=dict)
    supply: dict[str, Any] = field(default_factory=dict)
    plan: dict[str, list[str]] | None = None
