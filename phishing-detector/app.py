"""Flask API exposing the phishing-detection pipeline."""
from __future__ import annotations

import logging

import tldextract
from flask import Flask, jsonify, request
from flask_cors import CORS

from config import Config
from detector.domain_reputation import DomainReputationChecker
from detector.fusion import fuse_signals
from detector.model import PhishingModel
from detector.url_features import URLFeatureExtractor

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Required so the browser extension can call this API cross-origin.

# Loaded once at startup - these hold no per-request state, so they're
# safe to share across requests/threads.
_feature_extractor = URLFeatureExtractor()
_model = PhishingModel(Config.MODEL_PATH)
_reputation_checker = DomainReputationChecker(
    threat_intel_api_key=Config.THREAT_INTEL_API_KEY,
    threat_intel_api_url=Config.THREAT_INTEL_API_URL,
)


@app.route("/api/predict", methods=["POST"])
def predict():
    """Analyze a URL and return a phishing verdict.

    Expects JSON body: {"url": "https://example.com/path"}

    Returns:
        JSON response with verdict, confidence, and per-layer signal detail.
    """
    payload = request.get_json(silent=True)
    if not payload or "url" not in payload:
        return jsonify({"error": "Request body must include a 'url' field."}), 400

    url = payload["url"]

    try:
        features = _feature_extractor.extract(url)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    ml_probability = _model.predict_proba(features)

    domain = tldextract.extract(url).registered_domain
    recently_registered = _reputation_checker.is_recently_registered(domain)
    threat_intel = _reputation_checker.check_threat_intel(domain)

    result = fuse_signals(
        ml_probability=ml_probability,
        is_recently_registered=recently_registered,
        threat_intel_score=threat_intel["score"],
    )

    logger.info(
        "Predicted %s for %s (confidence=%.2f)",
        result["verdict"], url, result["confidence"],
    )

    return (
        jsonify(
            {
                "url": url,
                "verdict": result["verdict"],
                "confidence": result["confidence"],
                "signals": {
                    "ml_probability": round(ml_probability, 4),
                    "domain_recently_registered": recently_registered,
                    "threat_intel": threat_intel,
                },
            }
        ),
        200,
    )


@app.route("/health", methods=["GET"])
def health():
    """Basic liveness check for load balancers / uptime monitors."""
    return jsonify({"status": "ok"}), 200


if __name__ == "__main__":
    # Development only - use gunicorn (see README.md) in production.
    app.run(host="0.0.0.0", port=5000, debug=False)
