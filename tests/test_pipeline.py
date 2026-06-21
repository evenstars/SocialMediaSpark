"""End-to-end: the pipeline produces outputs and the guardrails are enforced."""
import config
from studio.graph import build_graph, new_job
from tests._helpers import sample_setup


def _run():
    deps, base = sample_setup()
    app = build_graph(deps)
    return app.invoke(new_job("professional headshot, dark background", "me", base))


def test_pipeline_produces_approved_outputs():
    state = _run()
    assert len(state["approved"]) >= 1
    assert len(state["exported"]) == len(state["approved"])


def test_gate_rejects_the_drifted_candidate():
    # generate makes 4 candidates, 1 deliberately drifted -> at most 3 approved
    state = _run()
    assert len(state["approved"]) < 4


def test_all_approved_meet_identity_threshold():
    state = _run()
    for c in state["approved"]:
        assert c.scores["identity"] >= config.ID_THRESHOLD


def test_all_approved_carry_content_credentials():
    state = _run()
    for c in state["approved"]:
        assert c.credentials and c.credentials["standard"] == "C2PA"
