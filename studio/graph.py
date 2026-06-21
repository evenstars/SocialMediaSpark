"""Orchestration: wire the five nodes into one pipeline, inject dependencies,
and provide a dependency-free fallback executor.

Pipeline (fixed order):
    ingest -> generate -> quality_gate -> review -> curate

Design notes:
- Each node has the shape `fn(state, deps) -> dict` (a partial state update).
- build_graph() binds a Deps object into every node, producing `state -> update`
  callables, then wires them with LangGraph (if installed) or the local
  sequential executor. Both expose `.invoke(state) -> state`.
- List fields (e.g. log) return the *full new list*, so behaviour is identical
  under LangGraph's overwrite merge and the fallback's dict.update.
"""
from __future__ import annotations

from typing import Optional

from studio.deps import Deps, default_deps
from studio.nodes.curate import curate
from studio.nodes.generate import generate
from studio.nodes.ingest import ingest
from studio.nodes.quality_gate import quality_gate
from studio.nodes.review import review
from studio.state import JobState

# Fixed order of pipeline nodes (name -> function taking (state, deps))
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


def build_pipeline(deps: Deps):
    """Bind deps into each node, yielding (name, state->update) callables."""
    return [(name, lambda state, fn=fn: fn(state, deps)) for name, fn in PIPELINE]


class _SequentialApp:
    """Fallback executor: run the bound pipeline in order, merge via dict.update.

    Interface mirrors a compiled LangGraph app's `.invoke`.
    """

    def __init__(self, bound_pipeline):
        self._pipeline = bound_pipeline

    def invoke(self, state: dict) -> dict:
        state = dict(state)               # do not mutate the caller's object
        for name, fn in self._pipeline:
            update = fn(state) or {}
            state.update(update)
        return state


def build_graph(deps: Optional[Deps] = None):
    """Build a runnable pipeline app (exposes `.invoke(state)`).

    deps defaults to stub models + local stores. With langgraph -> compiled
    StateGraph; otherwise -> _SequentialApp.
    """
    deps = deps or default_deps()
    bound = build_pipeline(deps)

    if langgraph_available():
        print("[graph] LangGraph available — building StateGraph")
        from langgraph.graph import END, START, StateGraph

        g = StateGraph(JobState)
        for name, fn in bound:
            g.add_node(name, fn)
        g.add_edge(START, bound[0][0])                    # entry
        for (a, _), (b, _) in zip(bound, bound[1:]):
            g.add_edge(a, b)                              # sequential edges
        g.add_edge(bound[-1][0], END)                     # exit
        return g.compile()

    print("[graph] LangGraph not available — falling back to SequentialApp")
    return _SequentialApp(bound)


def new_job(request: str, person_id: str, base_paths: list[str] | None = None) -> JobState:
    """Build an initial JobState (handy for cli / tests)."""
    return {
        "request": request,
        "person_id": person_id,
        "base_paths": base_paths or [],
        "log": [],
    }
