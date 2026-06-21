"""Guardrails: encode "legitimate" in code (threshold checks, content
credentials, explicit refusal of banned capabilities).

TODO(M3):
- identity_similarity / evaluate(candidate, identity) -> (pass?, reason)
- combined_score(candidate)
- attach_content_credentials(candidate)  # write only, never remove
- assert_capability_allowed(name)        # raise for watermark removal / multi-account / bulk publish

Thresholds and switches come from config.py.
"""
