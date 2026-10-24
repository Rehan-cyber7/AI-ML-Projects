"""Lexical and structural feature extraction from URLs.

No network calls are made here - every feature is derived from the URL
string itself, so extraction is fast and safe to run on untrusted input.
"""
from __future__ import annotations

import ipaddress
import logging
import re
from urllib.parse import urlparse

import tldextract

logger = logging.getLogger(__name__)

# Use tldextract's bundled public-suffix-list snapshot instead of fetching
# a live copy over the network. This keeps feature extraction genuinely
# network-free (important both for offline use and for avoiding a slow,
# unnecessary HTTP call on every single extraction).
_tld_extractor = tldextract.TLDExtract(suffix_list_urls=())

# Common URL-shortening services abused to obscure the true destination.
_SHORTENER_DOMAINS = frozenset(
    {
        "bit.ly", "tinyurl.com", "goo.gl", "t.co", "ow.ly",
        "is.gd", "buff.ly", "adf.ly", "rebrand.ly",
    }
)

# Words that appear disproportionately often in phishing URLs, typically
# to impersonate a login/verification flow.
_SUSPICIOUS_KEYWORDS = frozenset(
    {
        "secure", "account", "update", "verify", "login", "signin",
        "banking", "confirm", "webscr", "suspend", "password", "urgent",
    }
)


class URLFeatureExtractor:
    """Extracts a fixed-schema feature dict from a single URL."""

    def extract(self, url: str) -> dict[str, float | int | str]:
        """Extract all features for a given URL.

        Args:
            url: The raw URL string to analyze.

        Returns:
            A dict mapping feature names to numeric values. The schema is
            stable across calls, which is required for consistent model
            training/inference.

        Raises:
            ValueError: If the URL cannot be parsed at all (e.g. empty
                string or missing scheme/netloc after normalization).
        """
        normalized_url = self._normalize(url)
        parsed = urlparse(normalized_url)

        if not parsed.netloc:
            raise ValueError(f"Could not parse a valid host from URL: {url!r}")

        extracted = _tld_extractor(normalized_url)
        registered_domain = extracted.registered_domain
        hostname = parsed.hostname or ""

        features: dict[str, float | int | str] = {
            "url_length": len(normalized_url),
            "hostname_length": len(hostname),
            "path_length": len(parsed.path),
            "num_dots": normalized_url.count("."),
            "num_hyphens": normalized_url.count("-"),
            "num_underscores": normalized_url.count("_"),
            "num_slashes": normalized_url.count("/"),
            "num_digits": sum(char.isdigit() for char in normalized_url),
            "num_subdomains": (
                len(extracted.subdomain.split(".")) if extracted.subdomain else 0
            ),
            "has_at_symbol": int("@" in normalized_url),
            "has_ip_address": int(self._is_ip_address(hostname)),
            "uses_https": int(parsed.scheme == "https"),
            "is_shortened": int(registered_domain in _SHORTENER_DOMAINS),
            "has_suspicious_keyword": int(
                self._contains_suspicious_keyword(normalized_url)
            ),
            "has_double_slash_redirect": int("//" in parsed.path),
            "digit_ratio": (
                sum(char.isdigit() for char in normalized_url) / len(normalized_url)
                if normalized_url
                else 0.0
            ),
            "tld_length": len(extracted.suffix),
        }
        return features

    def extract_batch(self, urls: list[str]) -> list[dict[str, float | int | str]]:
        """Extract features for a list of URLs, skipping unparseable ones.

        Args:
            urls: List of raw URL strings.

        Returns:
            List of feature dicts, in the same order as valid input URLs
            (malformed URLs are dropped, with a warning logged).
        """
        results: list[dict[str, float | int | str]] = []
        for url in urls:
            try:
                results.append(self.extract(url))
            except ValueError:
                logger.warning("Skipping unparseable URL: %s", url)
        return results

    @staticmethod
    def _normalize(url: str) -> str:
        """Ensure the URL has a scheme so urlparse behaves predictably.

        Args:
            url: Raw URL, possibly missing a scheme (e.g. 'example.com').

        Returns:
            URL guaranteed to start with 'http://' or 'https://'.
        """
        stripped = url.strip()
        if not re.match(r"^https?://", stripped, re.IGNORECASE):
            stripped = f"http://{stripped}"
        return stripped

    @staticmethod
    def _is_ip_address(hostname: str) -> bool:
        """Check whether a hostname is a literal IPv4/IPv6 address.

        Args:
            hostname: The host component of a parsed URL.

        Returns:
            True if hostname is a valid IP literal, False otherwise.
        """
        try:
            ipaddress.ip_address(hostname)
            return True
        except ValueError:
            return False

    @staticmethod
    def _contains_suspicious_keyword(url: str) -> bool:
        """Check whether the URL contains common phishing-lure keywords.

        Args:
            url: Full URL string to scan.

        Returns:
            True if any keyword from _SUSPICIOUS_KEYWORDS appears.
        """
        lowered = url.lower()
        return any(keyword in lowered for keyword in _SUSPICIOUS_KEYWORDS)
