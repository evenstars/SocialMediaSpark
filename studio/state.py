"""数据契约：在 LangGraph 节点间流动的状态与核心数据对象。

Asset = 用户的真实底图；Candidate = 增强 / 生成出来的候选成片。
JobState 是流水线状态（LangGraph 用 TypedDict，节点返回部分更新并合并）。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional, TypedDict

import numpy as np


@dataclass
class Asset:
    """一张真实底图及其元数据。"""
    id: str
    path: str
    tags: dict[str, Any] = field(default_factory=dict)
    identity_vec: Optional[np.ndarray] = None     # 该图的人脸向量


@dataclass
class Candidate:
    """一张候选成片（来自增强或一致性生成）。"""
    id: str
    path: str
    source_asset_id: str
    latent: np.ndarray                            # 身份隐向量（真实实现里来自像素）
    scores: dict[str, float] = field(default_factory=dict)
    credentials: Optional[dict[str, Any]] = None  # C2PA 内容凭证（过闸后写入）
    status: str = "candidate"                     # candidate / rejected / approved
    needs_human: bool = True                      # v1：自动过闸后仍标记待人工确认
    reject_reason: Optional[str] = None


class JobState(TypedDict, total=False):
    request: str                  # 用户需求，如"深色背景的职业头像"
    person_id: str                # 身份标识（决定身份向量）
    base_paths: list[str]         # 真实底图路径
    assets: list[Asset]
    identity: np.ndarray          # 聚合后的身份基准向量
    candidates: list[Candidate]
    approved: list[Candidate]
    collection: str               # 入库到哪个用途集合
    exported: list[str]
    log: list[str]
