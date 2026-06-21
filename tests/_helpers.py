"""Shared test helpers (not test cases). Build a temp workspace with sample photos."""
from __future__ import annotations

import tempfile
from pathlib import Path

from PIL import Image

from studio.deps import Deps, default_deps


def make_base_images(dir_path: Path, n: int = 3) -> list[str]:
    """Create n distinct small PNGs and return their paths."""
    dir_path.mkdir(parents=True, exist_ok=True)
    paths = []
    for i in range(n):
        p = dir_path / f"me_{i}.png"
        Image.new("RGB", (64, 64), (40 + i * 30, 80, 120)).save(p)
        paths.append(str(p))
    return paths


def sample_setup() -> tuple[Deps, list[str]]:
    """A temp data dir with deps wired and a few base photos ready to ingest."""
    tmp = Path(tempfile.mkdtemp(prefix="sms_test_"))
    deps = default_deps(tmp)
    base = make_base_images(tmp / "base", n=3)
    return deps, base
