"""让测试能直接 `import config` / `import studio`（把仓库根加入 sys.path）。"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
