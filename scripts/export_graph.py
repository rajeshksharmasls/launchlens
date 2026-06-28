import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.launchlens.graph import build_graph


if __name__ == "__main__":
    graph = build_graph()
    mermaid = graph.get_graph().draw_mermaid()
    print(mermaid)
    Path(PROJECT_ROOT / "docs" / "graph.mmd").write_text(mermaid, encoding="utf-8")
