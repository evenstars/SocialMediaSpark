"""Guardrail unit tests: identity similarity, gate decisions, credentials, bans."""
import numpy as np
import pytest

import config
from studio import guardrails
from studio.state import Candidate


def _candidate(**scores) -> Candidate:
    c = Candidate(id="x", path="p", source_asset_id="a", latent=np.ones(4))
    c.scores = scores
    return c


def test_identity_similarity_range():
    v = np.array([1.0, 0.0, 0.0])
    assert guardrails.identity_similarity(v, v) == pytest.approx(1.0)
    assert guardrails.identity_similarity(v, -v) == pytest.approx(0.0)


def test_evaluate_rejects_low_identity():
    c = _candidate(identity=0.4, naturalness=0.9, aesthetic=0.8)
    ok, reason = guardrails.evaluate(c, np.ones(4))
    assert ok is False and "identity" in reason


def test_evaluate_rejects_low_naturalness():
    c = _candidate(identity=0.9, naturalness=0.3, aesthetic=0.8)
    ok, reason = guardrails.evaluate(c, np.ones(4))
    assert ok is False and "naturalness" in reason


def test_evaluate_passes_good_candidate():
    c = _candidate(identity=0.9, naturalness=0.9, aesthetic=0.8)
    ok, reason = guardrails.evaluate(c, np.ones(4))
    assert ok is True and reason is None


def test_attach_content_credentials():
    c = _candidate(identity=0.9, naturalness=0.9, aesthetic=0.8)
    guardrails.attach_content_credentials(c)
    assert c.credentials and c.credentials["standard"] == "C2PA"


def test_banned_capability_raises():
    for name in ("watermark_removal", "multi_account", "bulk_publish"):
        with pytest.raises(PermissionError):
            guardrails.assert_capability_allowed(name)
