"""护栏：把"正当"写进代码（阈值校验、内容凭证、被禁能力的显式拒绝）。

TODO(M2)：
- identity_similarity / evaluate(candidate, identity) -> (放行?, 原因)
- combined_score(candidate)
- attach_content_credentials(candidate)  # 仅写入、永不移除
- assert_capability_allowed(name)        # 对去标识/多账号/批量发布显式报错

阈值与开关来自 config.py。
"""
