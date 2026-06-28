from __future__ import annotations

from ..settings import PROJECT_ROOT

try:
    from langgraph.checkpoint.sqlite import SqliteSaver
except ImportError:  # pragma: no cover
    try:
        from langgraph.checkpoints.sqlite import SqliteSaver
    except ImportError:  # pragma: no cover
        SqliteSaver = None


def get_checkpointer():
    if SqliteSaver is None:
        return None
    return SqliteSaver.from_conn_string(str(PROJECT_ROOT / "checkpoints.sqlite"))
