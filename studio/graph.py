"""LangGraph 编排装配 + 无依赖 fallback 执行器。

TODO(M2)：
- build_graph()：用 langgraph.StateGraph 接线 ingest→generate→quality_gate→review→curate。
- 当 langgraph 不可用时，提供等价的顺序执行器（同样的节点签名），便于受限环境/测试运行。
"""
