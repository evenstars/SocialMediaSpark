"""全局配置：路径、护栏阈值、合规开关。

护栏相关常量集中在此，便于审计与代码评审。运行时不提供"悄悄关闭"的入口。
"""
from pathlib import Path

# ---- 存储路径（本地优先；云端实现通过环境变量覆盖）----
ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
FILES_DIR = DATA_DIR / "files"          # 原图 / 成片
DB_PATH = DATA_DIR / "library.db"       # SQLite 元数据（v1）
VECTOR_PATH = DATA_DIR / "vectors.npz"  # numpy 向量库（v1）

# ---- 护栏阈值 ----
ID_THRESHOLD = 0.65   # 成片与真实身份的最低相似度：低于则判定"不像本人"，拒绝
NAT_MIN = 0.60        # 自然度下限：拦截过度磨皮 / 明显伪影
AES_MIN = 0.40        # 美学下限（较宽松，主要靠人工复核）

# 综合排序权重（身份保真权重最高：优先"还是你"而非"更好看"）
SCORE_WEIGHTS = {"identity": 0.5, "aesthetic": 0.3, "naturalness": 0.2}

# ---- 合规开关（这些能力一律不提供，常量化以示明确）----
ALLOW_WATERMARK_REMOVAL = False     # 永不去除 / 覆盖 AI 标识
ALLOW_MULTI_ACCOUNT = False         # 不支持多账号 / 养号
ALLOW_BULK_PUBLISH = False          # 不支持批量自动发布
CONTENT_CREDENTIALS_REQUIRED = True # 重度增强 / 生成成片必须写入内容凭证


def ensure_dirs() -> None:
    """创建本地数据目录（按需调用，导入时不产生副作用）。"""
    FILES_DIR.mkdir(parents=True, exist_ok=True)
