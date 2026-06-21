"""Data contracts: the state flowing between LangGraph nodes, plus core objects.

Asset = a user's real source photo; Candidate = an enhanced/generated output.
JobState is the pipeline state (a TypedDict; nodes return partial updates that
are merged in).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional, TypedDict

import numpy as np


@dataclass
class Asset:
    """A real source photo and its metadata."""
    id: str
    path: str
    tags: dict[str, Any] = field(default_factory=dict)
    identity_vec: Optional[np.ndarray] = None     # face vector of this photo


@dataclass
class Candidate:
    """A candidate output (from enhancement or consistent generation)."""
    id: str
    path: str
    source_asset_id: str
    latent: np.ndarray                            # identity latent (from pixels in real impl)
    scores: dict[str, float] = field(default_factory=dict)
    credentials: Optional[dict[str, Any]] = None  # C2PA content credentials (set after gate)
    status: str = "candidate"                     # candidate / rejected / approved
    needs_human: bool = True                      # v1: still flag for human confirm after gate
    reject_reason: Optional[str] = None


class JobState(TypedDict, total=False):
    request: str                  # user request, e.g. "professional headshot, dark background"
    person_id: str                # identity key (determines the identity vector)
    base_paths: list[str]         # real source photo paths
    assets: list[Asset]
    identity: np.ndarray          # aggregated identity reference vector
    candidates: list[Candidate]
    approved: list[Candidate]
    collection: str               # which usage collection to file into
    exported: list[str]
    log: list[str]
