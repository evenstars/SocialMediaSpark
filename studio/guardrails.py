"""Guardrails: encode "legitimate" in code.

Single place allowed to decide pass/reject and to write content credentials.
Thresholds and switches come from config.py.
"""
from __future__ import annotations

import datetime as _dt
from typing import Optional

import numpy as np

import config
from studio.state import Candidate


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    if na == 0 or nb == 0:
        return 0.0
    return float(np.dot(a, b) / (na * nb))


def identity_similarity(candidate_vec: np.ndarray, identity: np.ndarray) -> float:
    """Similarity between an output and the real identity, mapped to [0, 1]."""
    return (cosine(candidate_vec, identity) + 1.0) / 2.0


def evaluate(candidate: Candidate, identity: np.ndarray) -> tuple[bool, Optional[str]]:
    """Apply all guardrails to one candidate. Returns (passed, reject_reason)."""
    sim = candidate.scores.get("identity", 0.0)
    nat = candidate.scores.get("naturalness", 0.0)
    aes = candidate.scores.get("aesthetic", 0.0)

    if sim < config.ID_THRESHOLD:
        return False, f"identity {sim:.2f} < {config.ID_THRESHOLD} (not enough like you)"
    if nat < config.NAT_MIN:
        return False, f"naturalness {nat:.2f} < {config.NAT_MIN} (over-smoothing/artifacts)"
    if aes < config.AES_MIN:
        return False, f"aesthetic {aes:.2f} < {config.AES_MIN}"
    return True, None


def combined_score(candidate: Candidate) -> float:
    w = config.SCORE_WEIGHTS
    s = candidate.scores
    return (
        w["identity"] * s.get("identity", 0.0)
        + w["aesthetic"] * s.get("aesthetic", 0.0)
        + w["naturalness"] * s.get("naturalness", 0.0)
    )


def attach_content_credentials(candidate: Candidate) -> Candidate:
    """Write (never remove) AI content credentials. Real impl signs via C2PA."""
    if not config.CONTENT_CREDENTIALS_REQUIRED:
        return candidate
    candidate.credentials = {
        "standard": "C2PA",
        "claim": "AI-enhanced from the user's own real photo",
        "source_asset_id": candidate.source_asset_id,
        "signed_at": _dt.datetime.now(_dt.timezone.utc).isoformat(),
    }
    return candidate


def assert_capability_allowed(name: str) -> None:
    """Raise for banned capabilities — block misuse at the code level."""
    banned = {
        "watermark_removal": config.ALLOW_WATERMARK_REMOVAL,
        "multi_account": config.ALLOW_MULTI_ACCOUNT,
        "bulk_publish": config.ALLOW_BULK_PUBLISH,
    }
    if name in banned and not banned[name]:
        raise PermissionError(f"capability '{name}' is forbidden by project guardrails")
