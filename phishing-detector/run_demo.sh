#!/usr/bin/env bash
# One-shot demo: install deps, generate synthetic data, train a model,
# run tests, and start the Flask API.
#
# Usage: ./run_demo.sh
set -euo pipefail

echo "==> Creating virtual environment (venv/)"
python3 -m venv venv
source venv/bin/activate

echo "==> Installing dependencies"
pip install --upgrade pip
pip install -r requirements.txt

echo "==> Generating synthetic sample dataset"
python scripts/generate_sample_data.py --output data/raw/sample_dataset.csv --count 500

echo "==> Preparing feature dataset"
python scripts/prepare_dataset.py --input data/raw/sample_dataset.csv --output data/processed/features.csv

echo "==> Training model"
python scripts/train_model.py --data data/processed/features.csv --output models/phishing_model.joblib

echo "==> Running tests"
pytest tests/ -v

echo "==> Starting Flask API on http://localhost:5000"
echo "    Try: curl -X POST http://localhost:5000/api/predict -H 'Content-Type: application/json' -d '{\"url\": \"http://verify-account-secure.example/login\"}'"
python app.py
