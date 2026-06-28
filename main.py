import sys

from src.launchlens.graph import build_graph, run_cli
from src.launchlens.nodes.router import classify_intent
from src.launchlens.nodes.summarizer import summarize_messages
from src.launchlens.tools.serpapi_tools import build_research_plan


__all__ = [
    "build_graph",
    "build_research_plan",
    "classify_intent",
    "run_cli",
    "summarize_messages",
]


def main() -> None:
    if len(sys.argv) > 1 and sys.argv[1] in {"--cli", "cli"}:
        run_cli()
        return

    print("LaunchLens CLI ready. Run 'python main.py --cli' to start the chat loop.")


if __name__ == "__main__":
    main()
