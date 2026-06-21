"""M2 acceptance: orchestration skeleton invokes; five nodes run in order, state threads through."""
from studio.graph import PIPELINE, build_graph, new_job


def test_pipeline_order_is_fixed():
    assert [name for name, _ in PIPELINE] == [
        "ingest", "generate", "quality_gate", "review", "curate",
    ]


def test_invoke_runs_all_nodes_in_order():
    app = build_graph()
    state = app.invoke(new_job("professional headshot, dark background", person_id="me"))
    # each node leaves one log line, in fixed order
    stages = [line.split(":")[0] for line in state["log"]]
    assert stages == ["ingest", "generate", "quality_gate", "review", "curate"]


def test_state_threads_through():
    app = build_graph()
    state = app.invoke(new_job("portfolio", person_id="me"))
    # initial fields kept + fields each node initializes are present
    assert state["request"] == "portfolio"
    assert state["person_id"] == "me"
    for key in ("assets", "candidates", "approved", "exported"):
        assert key in state


def test_fallback_executor_works_without_langgraph():
    # fallback executor works on its own (independent of whether langgraph is installed)
    from studio.graph import _SequentialApp
    app = _SequentialApp(PIPELINE)
    state = app.invoke(new_job("headshot", person_id="me"))
    assert len(state["log"]) == 5
