"""Centralized configuration, loaded from environment variables."""
from __future__ import annotations

import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    """Application configuration sourced from environment variables."""

    MODEL_PATH: str = os.environ.get("MODEL_PATH", "models/phishing_model.joblib")
    THREAT_INTEL_API_KEY: str = os.environ.get("THREAT_INTEL_API_KEY", "[YOUR_API_KEY]")
    THREAT_INTEL_API_URL: str = os.environ.get(
        "THREAT_INTEL_API_URL", "https://your-threat-intel-provider.example/api/v3"
    )
    SCREENSHOT_API_KEY: str = os.environ.get("SCREENSHOT_API_KEY", "[YOUR_API_KEY]")
    SCREENSHOT_API_URL: str = os.environ.get(
        "SCREENSHOT_API_URL", "https://your-screenshot-provider.example/capture"
    )
    ENABLE_SCREENSHOT_LAYER: bool = (
        os.environ.get("ENABLE_SCREENSHOT_LAYER", "false").lower() == "true"
    )
