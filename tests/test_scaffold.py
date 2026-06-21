"""M1 验收：包可导入 + 护栏常量与接口契约就位。"""
import config


def test_guardrail_constants():
    assert 0 < config.ID_THRESHOLD <= 1
    assert 0 < config.NAT_MIN <= 1
    assert config.ALLOW_WATERMARK_REMOVAL is False
    assert config.ALLOW_MULTI_ACCOUNT is False
    assert config.ALLOW_BULK_PUBLISH is False
    assert config.CONTENT_CREDENTIALS_REQUIRED is True


def test_score_weights_sum_to_one():
    assert abs(sum(config.SCORE_WEIGHTS.values()) - 1.0) < 1e-9


def test_data_contracts_import():
    from studio.state import Asset, Candidate, JobState
    assert Asset and Candidate and JobState


def test_model_interfaces_present():
    from studio.models import interfaces as mi
    for name in ("Tagger", "FaceEmbedder", "Enhancer", "Scorer"):
        assert hasattr(mi, name)


def test_storage_interfaces_present():
    from studio.storage import interfaces as si
    for name in ("MetadataStore", "VectorStore", "FileStore"):
        assert hasattr(si, name)
