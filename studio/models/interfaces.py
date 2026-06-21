"""模型能力的抽象契约。

业务/节点只依赖这些接口；具体实现（stub / OpenAI API / 自托管）可替换，互不影响。
"""
from __future__ import annotations

from abc import ABC, abstractmethod

import numpy as np

from studio.state import Asset, Candidate


class Tagger(ABC):
    """图片 → 结构化标签（角度 / 光线 / 场景 / 表情 / 画质 等）。"""

    @abstractmethod
    def tag(self, image_path: str) -> dict: ...


class FaceEmbedder(ABC):
    """图片 → 人脸向量（embedding）。身份基准与护栏校验共用同一实现。"""

    @abstractmethod
    def embed(self, image_path: str) -> np.ndarray: ...


class Enhancer(ABC):
    """底图 + 身份向量 → 候选成片。

    M3 = 确定性 stub；M5 = 托管图像 API（如 OpenAI）；v2 = 自托管（SDXL+InstantID）。
    """

    @abstractmethod
    def generate(
        self,
        identity: np.ndarray,
        refs: list[Asset],
        n: int,
        request: str,
    ) -> list[Candidate]: ...


class Scorer(ABC):
    """候选成片 → 质量分。至少返回 {'naturalness': float, 'aesthetic': float}。"""

    @abstractmethod
    def score(self, candidate: Candidate) -> dict: ...
