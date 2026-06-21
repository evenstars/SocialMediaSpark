# SocialMediaSpark —— 项目计划与里程碑

> 一个 **真实社交资料库 Agent**：用你**本人的真实素材**，借助 AI 做高质量增强与风格统一，构建并长期维护属于你自己的、真实的个人形象与内容资料库（个人写真 / 职业头像 / 作品集 / 社交资料），供你自己的、单一的、真实的账号使用。
>
> 编排技术：**LangGraph**。本文件只定计划与里程碑，**不含代码**。

---

## 1. 愿景与定位

把零散的真实照片整理成结构化、可检索的资料库，并在"始终是你本人"的前提下，把照片修得更专业、风格更统一，最终输出可直接使用的高质量个人形象素材。

**核心原则（写进护栏，强制执行）：** 真实身份、不伪造经历、不批量养号、不做 AI 检测/水印规避、不以操纵他人为目的。

---

## 2. v1 范围

**目标：一个可演示的端到端 demo —— 真实出图 + 可视化复核。**

**做：**
- 用 LangGraph 串起完整流水线：摄取 → 生成/增强 → 真实性&质量闸门 → 人工复核 → 策展/导出。
- 先用「接口 + stub」把流水线与护栏跑通（离线、可测试），再接真实模型——降低风险。
- **真实出图（M5，API 优先）**：通过 `Enhancer` 接口调用托管图像 API（如 OpenAI 图像模型），无需自建 GPU；身份校验用轻量本地或云端人脸向量。
- **复核界面（M6）**：Gradio 简易 Web UI，可视化挑图与导出。
- 落地核心护栏：身份保真阈值、不可关闭的 AI 内容凭证、本地优先存储。
- 存储接口优先：v1 = SQLite + numpy + 本地文件。

**不做（明确排除）：**
- 任何去标识 / 去水印 / 规避 AI 检测能力。
- 多账号 / 养号 / 批量自动发布、平台对接。
- 自托管重型生成后端（SDXL + InstantID 自建）——推迟到有隐私/一致性/成本需求时（v2）。

---

## 3. 护栏（验收时逐条核对）

- 身份保真阈值：成片与真实你的相似度必须达标，杜绝"换成更好看的人"。
- 不可关闭的 AI 内容凭证：重度增强 / 生成成片一律写入 C2PA，系统不提供去标识功能。
- 单账号、人工触发：不内置多账号、不内置批量发帖。
- 不杜撰：内容基于真实信息。
- 隐私与同意：人脸数据本地优先、加密、可一键删除。

---

## 4. 里程碑

| 里程碑 | 目标 | 主要交付物 | 退出标准（Exit Criteria） | 预估 |
|--------|------|-----------|--------------------------|------|
| **M0 立项与计划** | 锁定范围、技术与里程碑 | 本计划、技术方案、仓库初始化 | 计划评审通过，仓库可用 | 0.5 周 |
| **M1 脚手架** | 可运行的工程骨架 | 目录结构、依赖、配置、README、CI 占位 | 干净环境可 `import`，配置/护栏常量就位 | 0.5 周 |
| **M2 编排骨架** | LangGraph 跑通空链路 | `state` + `graph` 装配 + fallback 执行器 | 空节点链可 `invoke` 并按序执行 | 1 周 |
| **M3 模块与 stub** | 五节点 + 存储 + 模型接口 | ingest/generate/quality_gate/review/curate + storage + interfaces/stubs | 各节点用 stub 单测通过 | 1.5 周 |
| **M4 端到端 + 护栏测试** | MVP 完整跑通 | CLI `--demo`、pytest | 端到端出成片清单；测试验证"低于阈值被拒""通过者必带凭证" | 1 周 |
| **M5 真实模型接入（API 优先）** | 用托管 API 产出真实成片 | `Enhancer`→图像 API（如 OpenAI）、`FaceEmbedder`→轻量本地/云端人脸向量、`Scorer` | 真实底图产出真实成片，护栏不变 | 1.5 周 |
| **M6 复核界面与导出** | 人工复核可视化 | Gradio 复核界面、用途集合导出（保留凭证） | 界面挑图、导出带凭证成片 | 1 周 |

> **v1 = M0–M6**（demo 目标：端到端可演示，含真实出图与复核界面）。M5 默认走托管 API；自托管模型（SDXL+InstantID）推迟到 v2。

---

## 5. 工作分解（v1，M1–M6）

- **M1 脚手架**：目录结构、`requirements.txt`、`config.py`（阈值/路径/合规开关）、README、（可选）CI 占位。
- **M2 编排骨架**：`state.py`（JobState/Asset/Candidate）、`graph.py`（LangGraph 装配 + 无依赖 fallback 执行器，便于本地/沙盒运行）。
- **M3 模块与 stub**：
  - 节点：`ingest`（打标 + 建身份参考）、`generate`（检索底图 + 增强/一致性生成）、`quality_gate`（相似度/自然度/美学 + 写凭证）、`review`（v1 自动过闸 + 标记待人工）、`curate`（集合 + 导出）。
  - 存储（**接口优先**，业务层只依赖接口）：
    - `MetadataStore` 接口：关系/元数据。v1 实现 = SQLite；云端实现 = PostgreSQL。
    - `VectorStore` 接口：embedding 的存取与相似度检索。v1 实现 = numpy（文件 + 内存计算）；云端实现 = Postgres + pgvector（或 Chroma/LanceDB）。
    - `FileStore` 接口：原图/成片。v1 = 本地文件；云端 = 对象存储（S3 等）。
  - 模型接口：`Tagger / FaceEmbedder / Enhancer / Scorer` + 确定性 stub。
- **M4 跑通 + 测试**：`cli.py --demo` 合成示例底图跑全链；`tests/` 验证护栏。
- **M5 真实模型接入（API 优先）**：实现 `Enhancer` 的图像 API 适配（如 OpenAI），`FaceEmbedder` 接入真实人脸向量（轻量本地 insightface 或云端人脸比对）；用真实照片跑通，护栏阈值在真实向量上重新校准。注意：API 密钥与隐私（见第 8 节）。
- **M6 复核界面与导出**：Gradio 简易界面浏览候选、挑选、归类到用途集合；导出成片并保留内容凭证。

---

## 6. 拟定目录结构（M1 落地，当前尚未创建）

```
SocialMediaSpark/
├── README.md
├── requirements.txt
├── config.py
├── cli.py                       # 端到端入口（demo）
├── app.py                       # M6：Gradio 复核界面
├── docs/
│   ├── PROJECT_PLAN.md          # 本文件
│   └── TECH_DESIGN.md           # 技术方案（从已有方案迁入）
├── studio/
│   ├── state.py
│   ├── graph.py                 # LangGraph 装配 + fallback
│   ├── guardrails.py
│   ├── nodes/ {ingest,generate,quality_gate,review,curate}.py
│   ├── models/
│   │   ├── interfaces.py        # Tagger/FaceEmbedder/Enhancer/Scorer 抽象
│   │   ├── stubs.py             # 离线可跑的确定性实现（M3/M4 + 测试）
│   │   ├── openai_enhancer.py   # M5：图像 API 适配
│   │   └── face_embedder.py     # M5：真实人脸向量（护栏用）
│   └── storage/
│       ├── interfaces.py        # MetadataStore / VectorStore / FileStore 抽象
│       ├── sqlite_store.py      # v1：SQLite 实现 MetadataStore
│       ├── numpy_vectors.py     # v1：numpy 实现 VectorStore
│       ├── local_files.py       # v1：本地文件实现 FileStore
│       └── postgres_store.py    # v2/云：Postgres(+pgvector) 实现（占位）
└── tests/
    └── test_pipeline.py
```

---

## 7. 技术选型（确定项 + 待定项）

- **确定**：Python、LangGraph（编排）、pytest。
- **存储（接口优先，便于上云）**：
  - 关系/元数据：`MetadataStore` 接口；v1 = SQLite，云端 = PostgreSQL。
  - 向量检索：`VectorStore` 接口；v1 = numpy，云端 = Postgres + pgvector（一库同时管关系与向量）或专用向量库（Chroma / LanceDB）。
  - 文件：`FileStore` 接口；v1 = 本地，云端 = 对象存储。
- **生成（M5，API 优先）**：托管图像 API（如 OpenAI 图像模型）经 `Enhancer` 接口接入；自托管（SDXL + InstantID）作为 v2 备选。
- **人脸相似度（护栏用）**：轻量本地模型（insightface 等）或云端人脸比对。
- **复核界面（M6）**：Gradio。
- **内容凭证**：c2patool / py-c2pa，并保留 API 自带的来源标识。

> 说明：embedding（嵌入向量）是人脸/图片的"数字指纹"（一串数字），用于身份校验与语义检索；v1 的 numpy 向量只是最轻量的占位实现，正式/云端用 pgvector 等替换，业务层因接口隔离无需改动。

> 隐私权衡：调用托管图像 API 会把真实人脸照片发给第三方。个人 demo 通常可接受；若涉及他人数据或上生产，优先自托管（v2），让人脸数据留在本地。API 密钥用环境变量管理，不入库。

---

## 8. 风险与对策

| 风险 | 对策 |
|------|------|
| 重型依赖在受限环境装不上 | LangGraph 自带 fallback 执行器；模型一律走接口，stub 可独立跑 |
| 增强过度"不像本人" | 身份保真阈值硬拦截 + 自然度评分（M3/M4 测试覆盖） |
| 生物特征数据风险 | 本地优先、加密、可删除（M1 配置 + M5 落实） |
| 被误用 | 不实现去标识/养号/批量；护栏常量化并有显式拒绝 |
| API 身份一致性弱（出图不够像本人） | 用真实人脸向量在闸门处硬卡阈值，不达标即拒；必要时 v2 换自托管 InstantID |
| 真实人脸发往第三方 API（隐私） | 个人 demo 接受；密钥用环境变量；他人数据/生产优先自托管 |
| 范围蔓延 | v1 限定 M0–M6（demo），自托管模型/平台对接推到 v2 |

---

## 9. 验收标准（v1 Done 的定义）
1. `python cli.py --demo` 在干净环境（stub）跑通整条链并输出成片清单。
2. `pytest` 通过：验证"身份相似度低于阈值的候选被拒"且"通过的候选都带内容凭证"。
3. **M5**：配置 API 密钥后，喂真实底图能产出真实成片，并通过同一套护栏。
4. **M6**：Gradio 界面能浏览候选、挑选、导出带内容凭证的成片。
5. 仓库内不存在任何去标识 / 去水印 / 多账号 / 批量发布能力。

---

## 10. 下一步
- 评审本计划（里程碑、预估、范围）。
- 通过后进入 **M1 脚手架**，再逐里程碑推进。
