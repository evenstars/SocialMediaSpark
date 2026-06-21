"""Global config: paths, guardrail thresholds, compliance switches.

Guardrail constants live here for easy audit/review. There is no runtime path
to silently disable them.
"""
from pathlib import Path

# ---- Storage paths (local-first; cloud impls override via env) ----
ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
FILES_DIR = DATA_DIR / "files"          # source photos / outputs
DB_PATH = DATA_DIR / "library.db"       # SQLite metadata (v1)
VECTOR_PATH = DATA_DIR / "vectors.npz"  # numpy vector store (v1)

# ---- Guardrail thresholds ----
ID_THRESHOLD = 0.65   # min similarity to the real identity; below = "not you", reject
NAT_MIN = 0.60        # naturalness floor; blocks over-smoothing / obvious artifacts
AES_MIN = 0.40        # aesthetic floor (loose; mainly left to human review)

# Combined ranking weights (identity weighted highest: "still you" over "prettier")
SCORE_WEIGHTS = {"identity": 0.5, "aesthetic": 0.3, "naturalness": 0.2}

# ---- Compliance switches (these capabilities are never provided) ----
ALLOW_WATERMARK_REMOVAL = False     # never strip / cover AI markers
ALLOW_MULTI_ACCOUNT = False         # no multi-account / account farming
ALLOW_BULK_PUBLISH = False          # no bulk auto publishing
CONTENT_CREDENTIALS_REQUIRED = True # enhanced/generated outputs must carry credentials


def ensure_dirs() -> None:
    """Create local data dirs (call on demand; no import-time side effects)."""
    FILES_DIR.mkdir(parents=True, exist_ok=True)
