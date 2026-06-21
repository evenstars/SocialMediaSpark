"""Node 3: authenticity & quality gate.

Score each candidate, apply guardrails, attach content credentials to passers.
Rejected candidates are dropped from the forward state (reason kept in log).
"""
from __future__ import annotations

from studio import guardrails
from studio.deps import Deps
from studio.state import JobState


def quality_gate(state: JobState, deps: Deps) -> dict:
    identity = state["identity"]
    passed = []
    rejected = []
    for c in state.get("candidates", []):
        scores = deps.scorer.score(c)
        scores["identity"] = guardrails.identity_similarity(c.latent, identity)
        c.scores = scores

        ok, reason = guardrails.evaluate(c, identity)
        if ok:
            guardrails.attach_content_credentials(c)
            passed.append(c)
        else:
            c.status = "rejected"
            c.reject_reason = reason
            rejected.append(c)
        deps.meta_store.save_candidate(c)

    passed.sort(key=guardrails.combined_score, reverse=True)
    log = state.get("log", []) + [
        f"quality_gate: {len(passed)} passed, {len(rejected)} rejected"
    ]
    return {"candidates": passed, "log": log}
