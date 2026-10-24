"""Train and evaluate a phishing-URL classifier on extracted features.

Usage:
    python scripts/train_model.py --data data/processed/features.csv \
        --output models/phishing_model.joblib
"""
from __future__ import annotations

import argparse
import logging
from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

logger = logging.getLogger(__name__)

_RANDOM_STATE = 42


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments.

    Returns:
        Parsed arguments with dataset and output model paths.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--data", type=Path, required=True, help="Processed feature CSV."
    )
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="Where to save the trained model (.joblib).",
    )
    parser.add_argument(
        "--test-size",
        type=float,
        default=0.2,
        help="Fraction of data held out for evaluation (default: 0.2).",
    )
    return parser.parse_args()


def load_dataset(path: Path) -> tuple[pd.DataFrame, pd.Series]:
    """Load a processed feature CSV and split into X, y.

    Args:
        path: Path to a CSV produced by scripts/prepare_dataset.py.

    Returns:
        Tuple of (feature DataFrame, label Series).

    Raises:
        ValueError: If the 'label' column is missing.
    """
    df = pd.read_csv(path)
    if "label" not in df.columns:
        raise ValueError("Dataset must contain a 'label' column (0/1).")

    features = df.drop(columns=["label"])
    labels = df["label"]
    return features, labels


def build_candidate_models() -> dict[str, Pipeline]:
    """Define candidate model pipelines to compare.

    Returns:
        Dict mapping a model name to an unfitted sklearn Pipeline.
    """
    return {
        "logistic_regression": Pipeline(
            steps=[
                ("scaler", StandardScaler()),
                ("clf", LogisticRegression(max_iter=1000, random_state=_RANDOM_STATE)),
            ]
        ),
        "random_forest": Pipeline(
            steps=[
                (
                    "clf",
                    RandomForestClassifier(
                        n_estimators=300,
                        max_depth=None,
                        min_samples_leaf=2,
                        n_jobs=-1,
                        random_state=_RANDOM_STATE,
                    ),
                ),
            ]
        ),
    }


def evaluate_model(
    name: str, model: Pipeline, X_test: pd.DataFrame, y_test: pd.Series
) -> float:
    """Evaluate a fitted model on held-out data and log a report.

    Args:
        name: Human-readable model name, for logging.
        model: A fitted sklearn Pipeline.
        X_test: Held-out feature matrix.
        y_test: Held-out true labels.

    Returns:
        ROC-AUC score on the test set.
    """
    predictions = model.predict(X_test)
    probabilities = model.predict_proba(X_test)[:, 1]
    auc = roc_auc_score(y_test, probabilities)

    logger.info("=== %s ===", name)
    logger.info("\n%s", classification_report(y_test, predictions))
    logger.info("ROC-AUC: %.4f", auc)
    return auc


def main() -> None:
    """Load data, train candidate models, keep the best, save it to disk."""
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
    )
    args = parse_args()

    X, y = load_dataset(args.data)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=args.test_size, random_state=_RANDOM_STATE, stratify=y
    )
    logger.info("Train/test split: %d / %d rows", len(X_train), len(X_test))

    best_name, best_model, best_auc = None, None, -1.0
    for name, model in build_candidate_models().items():
        model.fit(X_train, y_train)
        auc = evaluate_model(name, model, X_test, y_test)
        if auc > best_auc:
            best_name, best_model, best_auc = name, model, auc

    logger.info("Best model: %s (ROC-AUC=%.4f)", best_name, best_auc)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump({"model": best_model, "feature_names": list(X.columns)}, args.output)
    logger.info("Saved best model to %s", args.output)


if __name__ == "__main__":
    main()
