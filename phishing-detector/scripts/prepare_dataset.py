"""Transform a raw URL/label CSV into a feature-engineered training set.

Usage:
    python scripts/prepare_dataset.py --input [PATH_TO_DATASET] \
        --output data/processed/features.csv
"""
from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

import pandas as pd

# Allow running this script directly (as `python scripts/prepare_dataset.py`)
# by adding the project root to sys.path so `detector` is importable.
sys.path.append(str(Path(__file__).resolve().parent.parent))
from detector.url_features import URLFeatureExtractor  # noqa: E402

logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments.

    Returns:
        Parsed arguments containing input/output paths.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input",
        type=Path,
        required=True,
        help="Path to raw CSV with 'url' and 'label' columns.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="Path to write the processed, feature-engineered CSV.",
    )
    return parser.parse_args()


def build_feature_dataset(raw_df: pd.DataFrame) -> pd.DataFrame:
    """Apply feature extraction to every URL in the raw dataset.

    Args:
        raw_df: DataFrame with at least 'url' and 'label' columns.

    Returns:
        DataFrame of extracted features plus the original 'label' column.

    Raises:
        ValueError: If required columns are missing from raw_df.
    """
    required_columns = {"url", "label"}
    if not required_columns.issubset(raw_df.columns):
        missing = required_columns - set(raw_df.columns)
        raise ValueError(f"Raw dataset is missing required columns: {missing}")

    extractor = URLFeatureExtractor()
    feature_rows: list[dict[str, float | int | str]] = []

    for row in raw_df.itertuples(index=False):
        try:
            features = extractor.extract(row.url)
            features["label"] = row.label
            feature_rows.append(features)
        except ValueError:
            logger.warning("Skipping malformed URL: %s", row.url)
            continue

    logger.info("Built feature set for %d/%d URLs", len(feature_rows), len(raw_df))
    return pd.DataFrame(feature_rows)


def main() -> None:
    """Entry point: load raw data, extract features, write processed CSV."""
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
    )
    args = parse_args()

    if not args.input.exists():
        raise FileNotFoundError(f"Input dataset not found: {args.input}")

    raw_df = pd.read_csv(args.input)
    logger.info("Loaded %d raw rows from %s", len(raw_df), args.input)

    processed_df = build_feature_dataset(raw_df)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    processed_df.to_csv(args.output, index=False)
    logger.info("Wrote processed dataset to %s", args.output)


if __name__ == "__main__":
    main()
