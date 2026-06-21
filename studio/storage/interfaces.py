"""存储抽象契约。

业务层只依赖这些接口。v1：SQLite + numpy + 本地文件；v2/云：Postgres(+pgvector) + 对象存储。
更换实现时业务层零改动。
"""
from __future__ import annotations

from abc import ABC, abstractmethod

import numpy as np

from studio.state import Asset, Candidate


class MetadataStore(ABC):
    """关系/元数据：assets、candidates、collections。"""

    @abstractmethod
    def init_schema(self) -> None: ...

    @abstractmethod
    def save_asset(self, asset: Asset) -> None: ...

    @abstractmethod
    def save_candidate(self, candidate: Candidate) -> None: ...

    @abstractmethod
    def add_to_collection(self, collection: str, candidate_id: str) -> None: ...

    @abstractmethod
    def list_collection(self, collection: str) -> list[str]: ...


class VectorStore(ABC):
    """embedding 的存取与相似度检索。"""

    @abstractmethod
    def add(self, id: str, vec: np.ndarray) -> None: ...

    @abstractmethod
    def search(self, vec: np.ndarray, k: int = 5) -> list[tuple[str, float]]:
        """返回 [(id, 相似度)]，按相似度降序。"""

    @abstractmethod
    def save(self) -> None: ...

    @abstractmethod
    def load(self) -> None: ...


class FileStore(ABC):
    """原图 / 成片的存取。"""

    @abstractmethod
    def put(self, data: bytes, name: str) -> str:
        """写入并返回可访问路径/URL。"""

    @abstractmethod
    def path(self, name: str) -> str: ...
