from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parents[2]
FIXTURES_DIR = PROJECT_ROOT / "data" / "fixtures"


def get_setting(name: str, default: str | None = None) -> str | None:
    return os.getenv(name, default)
