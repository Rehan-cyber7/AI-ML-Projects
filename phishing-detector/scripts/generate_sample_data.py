"""Generate a synthetic labeled URL dataset for testing the pipeline.

Every URL uses domains/IPs reserved for documentation (RFC 2606 ".example"
/ ".test" / ".invalid" and RFC 5737 TEST-NET ranges), so nothing here
resolves to a real, live website. This lets you run the full
prepare -> train -> serve pipeline immediately, without needing to source
a real labeled dataset first. Swap in a real dataset (see README.md) for
anything beyond a functional smoke test.

Usage:
    python scripts/generate_sample_data.py --output data/raw/sample_dataset.csv --count 500
"""
from __future__ import annotations

import argparse
import logging
import random
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)

_RESERVED_TLDS = ["example", "test", "invalid"]
_LEGIT_WORDS = [
    "shop", "news", "mail", "docs", "cloud", "blog", "store", "portal",
    "media", "market", "photos", "travel", "recipes", "learn", "community",
]
_PHISH_KEYWORDS = [
    "secure", "verify", "update", "account", "login", "confirm", "suspend",
    "banking", "signin", "urgent", "password",
]
_BRAND_LOOKALIKES = [
    "paypa1", "amaz0n", "netfl1x", "app1e", "micros0ft", "faceb00k",
]
# RFC 5737 documentation-only IPv4 ranges - guaranteed non-routable to a
# real host.
_DOC_IP_PREFIXES = ["192.0.2", "198.51.100", "203.0.113"]


def _random_legit_url(rng: random.Random) -> str:
    """Build a synthetic, non-resolving 'legitimate-style' URL.

    Args:
        rng: Seeded Random instance for reproducibility.

    Returns:
        A synthetic https URL using a reserved TLD.
    """
    word = rng.choice(_LEGIT_WORDS)
    number = rng.randint(1, 999)
    tld = rng.choice(_RESERVED_TLDS)
    path_depth = rng.randint(0, 2)
    path = "/".join(rng.choice(["home", "about", "items", "page"]) for _ in range(path_depth))
    url = f"https://{word}{number}.{tld}"
    if path:
        url += f"/{path}"
    return url


def _random_phishing_url(rng: random.Random) -> str:
    """Build a synthetic, non-resolving 'phishing-style' URL.

    Mimics common phishing patterns (raw IPs, brand lookalikes, suspicious
    keywords, excessive hyphens/subdomains) using only reserved,
    non-resolving addresses/domains.

    Args:
        rng: Seeded Random instance for reproducibility.

    Returns:
        A synthetic http(s) URL exhibiting phishing-style structure.
    """
    style = rng.choice(["ip_based", "lookalike", "keyword_stuffed"])

    if style == "ip_based":
        prefix = rng.choice(_DOC_IP_PREFIXES)
        host = f"{prefix}.{rng.randint(1, 254)}"
        keyword = rng.choice(_PHISH_KEYWORDS)
        return f"http://{host}/{keyword}/{rng.choice(_PHISH_KEYWORDS)}.php"

    if style == "lookalike":
        brand = rng.choice(_BRAND_LOOKALIKES)
        keyword = rng.choice(_PHISH_KEYWORDS)
        tld = rng.choice(_RESERVED_TLDS)
        return f"http://{keyword}-{brand}.{tld}/{rng.choice(_PHISH_KEYWORDS)}"

    keywords = rng.sample(_PHISH_KEYWORDS, k=3)
    tld = rng.choice(_RESERVED_TLDS)
    return f"http://{'-'.join(keywords)}.{tld}/{rng.choice(_PHISH_KEYWORDS)}?id={rng.randint(1000,9999)}"


def generate_dataset(count: int, seed: int = 42) -> pd.DataFrame:
    """Generate a balanced synthetic dataset of legitimate/phishing URLs.

    Args:
        count: Total number of rows to generate (split ~50/50).
        seed: Random seed for reproducibility.

    Returns:
        DataFrame with 'url' and 'label' columns (label: 0=legit, 1=phishing).
    """
    rng = random.Random(seed)
    rows: list[dict[str, str | int]] = []

    for _ in range(count // 2):
        rows.append({"url": _random_legit_url(rng), "label": 0})
        rows.append({"url": _random_phishing_url(rng), "label": 1})

    rng.shuffle(rows)
    return pd.DataFrame(rows)


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments.

    Returns:
        Parsed arguments with output path and row count.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/raw/sample_dataset.csv"),
        help="Where to write the synthetic CSV.",
    )
    parser.add_argument(
        "--count", type=int, default=500, help="Total rows to generate."
    )
    return parser.parse_args()


def main() -> None:
    """Entry point: generate the synthetic dataset and write it to disk."""
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
    )
    args = parse_args()

    df = generate_dataset(args.count)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(args.output, index=False)
    logger.info("Wrote %d synthetic rows to %s", len(df), args.output)


if __name__ == "__main__":
    main()
