"""Load a trained phishing model and expose a simple predict() interface."""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import joblib
import pandas as pd

logger = logging.getLogger(__name__)


class PhishingModel:
    """Thin wrapper around a trained sklearn pipeline for inference."""

    def __init__(self, model_path: str | Path) -> None:
        """Load a serialized model bundle from disk.

        Args:
            model_path: Path to a .joblib file produced by train_model.py,
                containing {'model': Pipeline, 'feature_names': list[str]}.

        Raises:
            FileNotFoundError: If model_path does not exist.
        """
        model_path = Path(model_path)
        if not model_path.exists():
            raise FileNotFoundError(
                f"Model file not found: {model_path}. "
                "Run scripts/train_model.py first to generate it."
            )

        bundle: dict[str, Any] = joblib.load(model_path)
        self._model = bundle["model"]
        self._feature_names: list[str] = bundle["feature_names"]
        logger.info("Loaded model from %s", model_path)

    def predict_proba(self, features: dict[str, float | int | str]) -> float:
        """Predict the phishing probability for one feature dict.

        Args:
            features: Feature dict as produced by URLFeatureExtractor.extract.

        Returns:
            Probability (0.0-1.0) that the URL is phishing.

        Raises:
            ValueError: If features is missing any expected columns.
        """
        missing = set(self._feature_names) - set(features.keys())
        if missing:
            raise ValueError(f"Missing required features: {missing}")

        row = pd.DataFrame([{name: features[name] for name in self._feature_names}])
        probability = self._model.predict_proba(row)[0, 1]
        return float(probability)
