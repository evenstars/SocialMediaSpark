# SocialMediaSpark

一个 **真实社交资料库 Agent**：用你**本人的真实素材**，借助 AI 做高质量增强与风格统一，构建并长期维护属于你自己的、真实的个人形象资料库（写真 / 职业头像 / 作品集 / 社交资料），供你自己的、单一的、真实的账号使用。

编排技术：**LangGraph**。完整计划见 [`docs/PROJECT_PLAN.md`](docs/PROJECT_PLAN.md)。

## 原则（写进护栏，强制执行）
真实身份、不伪造经历、不批量养号、不做 AI 检测/水印规避、不以操纵他人为目的。

## 状态
- **M1 脚手架** ✅：目录结构、依赖、配置、接口契约、占位模块、导入测试。
- 后续：M2 编排骨架 → M3 模块与 stub → M4 端到端+护栏测试 → M5 真实模型(API) → M6 复核界面。

## 目录
```
config.py                # 路径 / 护栏阈值 / 合规开关
studio/
  state.py               # 数据契约：Asset / Candidate / JobState
  graph.py               # (M2) LangGraph 装配 + fallback 执行器
  guardrails.py          # (M2) 护栏：阈值校验 + 内容凭证
  nodes/                 # (M3) ingest/generate/quality_gate/review/curate
  models/
    interfaces.py        # Tagger/FaceEmbedder/Enhancer/Scorer 抽象
    stubs.py             # (M3) 离线可跑的确定性实现
  storage/
    interfaces.py        # MetadataStore/VectorStore/FileStore 抽象
    ...                  # (M3) sqlite / numpy / 本地文件实现；(v2) postgres
cli.py                   # (M4) 端到端 demo 入口
app.py                   # (M6) Gradio 复核界面
tests/                   # 测试
```

## 开发
```bash
pip install -r requirements.txt
pytest -q
```
