"""Orchestration skeleton: wire the five nodes into one pipeline,
plus a dependency-free fallback executor.

Pipeline (fixed order):
    ingest -> generate -> quality_gate -> review -> curate

Design notes:
- Every node has the same shape: `fn(state) -> dict` (returns a partial state
  update that the executor merges into state).
- Prefer LangGraph for wiring; if langgraph is not installed, use the local
  sequential executor. Both expose `.invoke(state) -> state`, so callers/tests
  don't care which one is used.
- List fields (e.g. log) return the *full new list*, so behaviour is identical
  under LangGraph's default overwrite merge and the fallback's dict.update.
  No custom reducer needed.
"""
from __future__ import annotations

from studio.nodes.curate import curate
from studio.nodes.generate import generate
from studio.nodes.ingest import ingest
from studio.nodes.quality_gate import quality_gate
from studio.nodes.review import review
from studio.state import JobState

# Fixed order of pipeline nodes (name -> function)
PIPELINE = [
    ("ingest", ingest),
    ("generate", generate),
    ("quality_gate", quality_gate),
    ("review", review),
    ("curate", curate),
]


def langgraph_available() -> bool:
    try:
        import langgraph.graph  # noqa: F401
        return True
    except ImportError:
        return False


class _SequentialApp:
    """Fallback executor: run PIPELINE in order, merge updates via dict.update.

    Intentionally implements only what a linear chain needs; the interface
    mirrors a compiled LangGraph app's `.invoke`.
    """

    def __init__(self, pipeline):
        self._pipeline = pipeline

    def invoke(self, state: dict) -> dict:
        state = dict(state)               # do not mutate the caller's object
        for name, fn in self._pipeline:
            update = fn(state) or {}
            state.update(update)
        return state


def build_graph():
    """Build and return a runnable pipeline app (exposes `.invoke(state)`).

    With langgraph -> compiled StateGraph; otherwise -> _SequentialApp.
    """
    if langgraph_available():
        print("[graph] LangGraph available — building StateGraph")
        from langgraph.graph import END, START, StateGraph

        g = StateGraph(JobState)
        for name, fn in PIPELINE:
            g.add_node(name, fn)
        g.add_edge(START, PIPELINE[0][0])                 # entry
        for (a, _), (b, _) in zip(PIPELINE, PIPELINE[1:]):
            g.add_edge(a, b)                              # sequential edges
        g.add_edge(PIPELINE[-1][0], END)                  # exit
        return g.compile()

    print("[graph] LangGraph not available — falling back to SequentialApp")
    return _SequentialApp(PIPELINE)


def new_job(request: str, person_id: str, base_paths: list[str] | None = None) -> JobState:
    """Build an initial JobState (handy for cli / tests)."""
    return {
        "request": request,
        "person_id": person_id,
        "base_paths": base_paths or [],
        "log": [],
    }
