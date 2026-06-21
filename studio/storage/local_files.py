"""Local filesystem implementation of FileStore (v1)."""
from __future__ import annotations

from pathlib import Path

from studio.storage.interfaces import FileStore


class LocalFileStore(FileStore):
    def __init__(self, base_dir: str | Path):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def put(self, data: bytes, name: str) -> str:
        dest = self.base_dir / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
        return str(dest)

    def path(self, name: str) -> str:
        return str(self.base_dir / name)
