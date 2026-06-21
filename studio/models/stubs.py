"""Deterministic, offline stub implementations of the four model interfaces.

No network/GPU. Good enough to run the whole pipeline and exercise the
guardrails. Real impls (OpenAI API / self-hosted) replace these in M5.

Key design for a meaningful gate:
- StubFaceEmbedder turns any image into a stable vector (seeded by file bytes).
- StubEnhancer makes most candidates close to the identity vector (will pass the
  identity gate) and deliberately makes one "drifted" candidate (will be rejected),
  so the guardrail is visibly doing its job.
"""
from __future__ import annotations

import hashlib
import io
import uuid

import numpy as np
from PIL import Image

import config
from studio.models.interfaces import Enhancer, FaceEmbedder, Scorer, Tagger
from studio.state import Asset, Candidate

VECTOR_DIM = 32


def _seed_from_bytes(data: bytes) -> int:
    return int.from_bytes(hashlib.sha256(data).digest()[:8], "big")


def _unit(vec: np.ndarray) -> np.ndarray:
    n = np.linalg.norm(vec)
    return vec if n == 0 else vec / n


class StubTagger(Tagger):
    """Derive simple tags from image brightness (deterministic)."""

    def tag(self, image_path: str) -> dict:
        img = Image.open(image_path).convert("L")
        brightness = float(np.asarray(img).mean()) / 255.0
        return {
            "lighting": "bright" if brightness > 0.6 else "natural",
            "brightness": round(brightness, 3),
        }


class StubFaceEmbedder(FaceEmbedder):
    """Stable vector seeded by file content (same file -> same vector)."""

    def embed(self, image_path: str) -> np.ndarray:
        with open(image_path, "rb") as f:
            seed = _seed_from_bytes(f.read())
        rng = np.random.default_rng(seed)
        return _unit(rng.standard_normal(VECTOR_DIM))


class StubEnhancer(Enhancer):
    """Produce candidate images near the identity, plus one drifted candidate.

    Needs a FileStore to write candidate images and a FaceEmbedder contract;
    here the candidate's identity vector is attached directly as `latent`
    (in a real impl it would be embedder.embed(generated_image)).
    """

    def __init__(self, file_store, drift_scale: float = 0.08):
        self.file_store = file_store
        self.drift_scale = drift_scale

    def generate(self, identity, refs: list[Asset], n: int, request: str) -> list[Candidate]:
        rng = np.random.default_rng(_seed_from_bytes(request.encode()))
        out: list[Candidate] = []
        for i in range(n):
            is_drift = (n >= 2 and i == n - 1)  # last one drifts -> should be rejected
            if is_drift:
                # opposite direction to identity -> similarity ~0 -> always rejected
                latent = _unit(-np.asarray(identity, dtype=float) + 0.02 * rng.standard_normal(VECTOR_DIM))
            else:
                latent = _unit(identity + self.drift_scale * rng.standard_normal(VECTOR_DIM))

            cid = uuid.uuid4().hex[:12]
            img = self._render(latent)
            path = self.file_store.put(img, f"cand_{cid}.png")
            src = refs[i % len(refs)].id if refs else "none"
            out.append(Candidate(id=cid, path=path, source_asset_id=src, latent=latent))
        return out

    @staticmethod
    def _render(latent: np.ndarray) -> bytes:
        # tiny solid-color image derived from the latent (just so a real file exists)
        rgb = tuple(int(x) for x in ((np.abs(latent[:3]) * 255) % 256).astype(int))
        buf = io.BytesIO()
        Image.new("RGB", (64, 64), rgb).save(buf, format="PNG")
        return buf.getvalue()


class StubScorer(Scorer):
    """Deterministic naturalness/aesthetic from the candidate id.

    Kept comfortably above the floors so that *identity* is the discriminating
    guardrail in the demo (naturalness failures are covered by unit tests).
    """

    def score(self, candidate: Candidate) -> dict:
        rng = np.random.default_rng(_seed_from_bytes(candidate.id.encode()))
        naturalness = float(0.70 + 0.25 * rng.random())   # 0.70 - 0.95
        aesthetic = float(0.55 + 0.35 * rng.random())     # 0.55 - 0.90
        return {"naturalness": round(naturalness, 3), "aesthetic": round(aesthetic, 3)}
