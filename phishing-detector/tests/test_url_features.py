"""Unit tests for detector.url_features.URLFeatureExtractor."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.append(str(Path(__file__).resolve().parent.parent))
from detector.url_features import URLFeatureExtractor  # noqa: E402


@pytest.fixture
def extractor() -> URLFeatureExtractor:
    """Provide a fresh extractor instance for each test."""
    return URLFeatureExtractor()


def test_extract_returns_expected_keys(extractor: URLFeatureExtractor) -> None:
    """extract() should return a dict with all expected feature keys."""
    features = extractor.extract("https://shop42.example/items")
    expected_keys = {
        "url_length", "hostname_length", "path_length", "num_dots",
        "num_hyphens", "num_underscores", "num_slashes", "num_digits",
        "num_subdomains", "has_at_symbol", "has_ip_address", "uses_https",
        "is_shortened", "has_suspicious_keyword", "has_double_slash_redirect",
        "digit_ratio", "tld_length",
    }
    assert expected_keys.issubset(features.keys())


def test_detects_ip_address_host(extractor: URLFeatureExtractor) -> None:
    """A raw IPv4 address in the host position should set has_ip_address=1."""
    features = extractor.extract("http://192.0.2.10/login")
    assert features["has_ip_address"] == 1


def test_detects_domain_host_as_non_ip(extractor: URLFeatureExtractor) -> None:
    """A normal domain name should set has_ip_address=0."""
    features = extractor.extract("https://news1.example/")
    assert features["has_ip_address"] == 0


def test_detects_at_symbol(extractor: URLFeatureExtractor) -> None:
    """URLs containing '@' should set has_at_symbol=1."""
    features = extractor.extract("http://example.test/@redirect")
    assert features["has_at_symbol"] == 1


def test_detects_https(extractor: URLFeatureExtractor) -> None:
    """uses_https should reflect the URL scheme."""
    assert extractor.extract("https://mail1.example/")["uses_https"] == 1
    assert extractor.extract("http://mail1.example/")["uses_https"] == 0


def test_detects_suspicious_keyword(extractor: URLFeatureExtractor) -> None:
    """Known phishing-lure keywords should be flagged."""
    features = extractor.extract("http://verify-account.example/confirm")
    assert features["has_suspicious_keyword"] == 1


def test_missing_scheme_is_normalized(extractor: URLFeatureExtractor) -> None:
    """URLs without a scheme should still parse (defaulting to http)."""
    features = extractor.extract("shop1.example/page")
    assert features["uses_https"] == 0
    assert features["hostname_length"] > 0


def test_raises_on_empty_string(extractor: URLFeatureExtractor) -> None:
    """An empty/unparseable string should raise ValueError."""
    with pytest.raises(ValueError):
        extractor.extract("")


def test_extract_batch_skips_invalid_urls(extractor: URLFeatureExtractor) -> None:
    """extract_batch should skip malformed entries rather than raising."""
    results = extractor.extract_batch(["https://mail2.example/", ""])
    assert len(results) == 1
