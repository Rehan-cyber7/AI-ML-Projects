# Phishing Website Detector

A multi-layered phishing detection system: URL feature analysis, a
Scikit-learn classifier, domain reputation lookups (WHOIS + threat-intel),
optional screenshot-based visual analysis, a Flask API, and a companion
browser extension.

## Quickstart (fastest path to a running demo)

```bash
chmod +x run_demo.sh
./run_demo.sh
```

This creates a virtualenv, installs dependencies, generates a **synthetic**
sample dataset (safe, non-resolving `.example`/`.test` domains and
RFC 5737 documentation IPs — nothing here points at a real site), trains a
model, runs the test suite, and starts the API on `http://localhost:5000`.

## Manual step-by-step

```bash
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env              # then edit .env with real API keys

# 1. Get labeled data. Either generate the synthetic demo set:
python scripts/generate_sample_data.py --output data/raw/sample_dataset.csv --count 500
# ...or drop a real dataset (see "Using a real dataset" below) at [PATH_TO_DATASET].

# 2. Turn raw URLs into model-ready features
python scripts/prepare_dataset.py --input data/raw/sample_dataset.csv --output data/processed/features.csv

# 3. Train the classifier
python scripts/train_model.py --data data/processed/features.csv --output models/phishing_model.joblib

# 4. Run tests
pytest tests/ -v

# 5. Start the API
python app.py
```

Test it:

```bash
curl -X POST http://localhost:5000/api/predict \
  -H "Content-Type: application/json" \
  -d '{"url": "http://verify-account-secure.example/login"}'
```

## Using a real dataset

Replace the synthetic generator with a real labeled source — PhishTank,
the UCI "Phishing Websites" dataset, or a Kaggle phishing-URL CSV — as long
as it has `url` and `label` (0/1) columns. Point `prepare_dataset.py --input`
at that file (`[PATH_TO_DATASET]`) instead of the synthetic CSV. Keep raw
datasets out of version control (`data/raw/` is already gitignored).

## Project layout

```
phishing-detector/
├── app.py                       # Flask API (orchestrates all layers)
├── config.py                    # Env-var driven configuration
├── requirements.txt
├── .env.example                 # Copy to .env and fill in real API keys
├── run_demo.sh                  # One-command end-to-end demo
│
├── detector/
│   ├── url_features.py          # Lexical/structural URL feature extraction
│   ├── model.py                 # Trained-model load + predict wrapper
│   ├── domain_reputation.py     # WHOIS age + threat-intel API lookups
│   ├── screenshot_analysis.py   # Visual brand-similarity layer (optional)
│   └── fusion.py                # Combines signals into a final verdict
│
├── scripts/
│   ├── generate_sample_data.py  # Synthetic demo dataset generator
│   ├── prepare_dataset.py       # Raw URLs -> feature CSV
│   └── train_model.py           # Train & evaluate the classifier
│
├── extension/                   # Manifest V3 browser extension
│   ├── manifest.json
│   ├── background.js
│   ├── content_script.js
│   └── popup/
│
├── tests/                       # pytest unit tests
├── docker/                      # Dockerfile + docker-compose.yml
├── data/{raw,processed}/
└── models/
```

## Enabling optional layers

- **Domain reputation**: works out of the box for WHOIS lookups (needs
  outbound network access). Set `THREAT_INTEL_API_KEY` /
  `THREAT_INTEL_API_URL` in `.env` to enable the external threat-intel call;
  it fails open (contributes a neutral score) if unset or unreachable.
- **Screenshot analysis**: not wired into `app.py`'s synchronous request
  path by design — it's the slowest layer (browser rendering + image
  hashing). See `detector/screenshot_analysis.py`; run it as a background
  job and build a `BrandTemplate` library from pages you want to protect
  before enabling it.

## Deploying the API

```bash
# Production WSGI server
gunicorn --workers 4 --bind 0.0.0.0:5000 --timeout 30 app:app

# Or via Docker
docker build -t phishing-detector -f docker/Dockerfile .
docker run -p 5000:5000 --env-file .env phishing-detector
# or: docker compose -f docker/docker-compose.yml up --build
```

Put a TLS-terminating reverse proxy (nginx, or a cloud load balancer) in
front of Gunicorn in any real deployment.

## Loading the browser extension (development)

1. Open `chrome://extensions`.
2. Enable "Developer mode".
3. Click "Load unpacked" and select the `extension/` folder.
4. Edit `API_ENDPOINT` in `extension/background.js` and
   `host_permissions` in `extension/manifest.json` to point at your
   deployed Flask API.

## Notes

- All API keys are read from environment variables via `.env`
  (`python-dotenv`) — never hardcoded. `.env` itself is gitignored;
  `.env.example` shows the expected shape with `[YOUR_API_KEY]` placeholders.
- The synthetic dataset uses only IANA/RFC-reserved documentation domains
  and IP ranges (`.example`, `.test`, `.invalid`, `192.0.2.0/24`,
  `198.51.100.0/24`, `203.0.113.0/24`), so nothing in this repo points at a
  real website.
- Train/serve consistency: `prepare_dataset.py` and `app.py` both import
  the same `detector.url_features.URLFeatureExtractor`, so training and
  live inference can never drift apart on feature logic.
