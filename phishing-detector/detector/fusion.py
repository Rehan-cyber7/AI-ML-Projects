"""Combine independent detection signals into a single verdict."""
from __future__ import annotations

# Weights reflect each layer's typical reliability; tune against your own
# validation set rather than treating these as fixed truths.
_WEIGHT_ML_MODEL = 0.5
_WEIGHT_DOMAIN_AGE = 0.2
_WEIGHT_THREAT_INTEL = 0.3

_PHISHING_THRESHOLD = 0.7
_SUSPICIOUS_THRESHOLD = 0.4


def fuse_signals(
    ml_probability: float,
    is_recently_registered: bool,
    threat_intel_score: float,
) -> dict[str, str | float]:
    """Combine detection signals into a final confidence score and verdict.

    Args:
        ml_probability: Phishing probability (0-1) from the ML classifier.
        is_recently_registered: Whether WHOIS flags the domain as new.
        threat_intel_score: Risk score (0-1) from the threat-intel API.

    Returns:
        Dict with 'confidence' (0-1 float) and 'verdict' (str).
    """
    domain_age_score = 1.0 if is_recently_registered else 0.0

    confidence = (
        _WEIGHT_ML_MODEL * ml_probability
        + _WEIGHT_DOMAIN_AGE * domain_age_score
        + _WEIGHT_THREAT_INTEL * threat_intel_score
    )
    confidence = round(min(max(confidence, 0.0), 1.0), 4)

    if confidence >= _PHISHING_THRESHOLD:
        verdict = "phishing"
    elif confidence >= _SUSPICIOUS_THRESHOLD:
        verdict = "suspicious"
    else:
        verdict = "legitimate"

    return {"confidence": confidence, "verdict": verdict}
