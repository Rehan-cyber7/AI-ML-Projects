"""Unit tests for detector.fusion.fuse_signals."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))
from detector.fusion import fuse_signals  # noqa: E402


def test_high_ml_probability_yields_phishing_verdict() -> None:
    """A high ML score alone should push the verdict toward phishing."""
    result = fuse_signals(
        ml_probability=0.95, is_recently_registered=True, threat_intel_score=0.9
    )
    assert result["verdict"] == "phishing"
    assert 0.0 <= result["confidence"] <= 1.0


def test_low_signals_yield_legitimate_verdict() -> None:
    """Low scores across all layers should yield a legitimate verdict."""
    result = fuse_signals(
        ml_probability=0.05, is_recently_registered=False, threat_intel_score=0.0
    )
    assert result["verdict"] == "legitimate"


def test_confidence_is_bounded() -> None:
    """Confidence should always be clamped to [0, 1] regardless of inputs."""
    result = fuse_signals(
        ml_probability=1.0, is_recently_registered=True, threat_intel_score=1.0
    )
    assert 0.0 <= result["confidence"] <= 1.0
