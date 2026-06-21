"""Orchestration: skeleton invokes; five nodes run in order, state threads through."""
from studio.graph import PIPELINE, _SequentialApp, build_graph, build_pipeline, new_job
from tests._helpers import sample_setup


def test_pipeline_order_is_fixed():
    assert [name for name, _ in PIPELINE] == [
        "ingest", "generate", "quality_gate", "review", "curate",
    ]


def test_invoke_runs_all_nodes_in_order():
    deps, base = sample_setup()
    app = build_graph(deps)
    state = app.invoke(new_job("professional headshot", person_id="me", base_paths=base))
    stages = [line.split(":")[0] for line in state["log"]]
    assert stages == ["ingest", "generate", "quality_gate", "review", "curate"]


def test_state_threads_through():
    deps, base = sample_setup()
    app = build_graph(deps)
    state = app.invoke(new_job("portfolio", person_id="me", base_paths=base))
    assert state["request"] == "portfolio"
    assert state["person_id"] == "me"
    for key in ("assets", "candidates", "approved", "exported"):
        assert key in state


def test_fallback_executor_works_without_langgraph():
    deps, base = sample_setup()
    app = _SequentialApp(build_pipeline(deps))
    state = app.invoke(new_job("headshot", person_id="me", base_paths=base))
    assert len(state["log"]) == 5
