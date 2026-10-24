"""Domain reputation checks: WHOIS registration age + threat-intel API."""
from __future__ import annotations

import logging
from datetime import datetime, timezone

import requests
import whois

logger = logging.getLogger(__name__)

_REQUEST_TIMEOUT_SECONDS = 5
_NEW_DOMAIN_THRESHOLD_DAYS = 90


class DomainReputationChecker:
    """Looks up WHOIS age and third-party threat-intel verdicts for a domain."""

    def __init__(self, threat_intel_api_key: str, threat_intel_api_url: str) -> None:
        """Configure the checker with threat-intel API credentials.

        Args:
            threat_intel_api_key: API key for your chosen threat-intel
                provider (e.g. [YOUR_API_KEY]). Load the real value from an
                environment variable at runtime - never hardcode it.
            threat_intel_api_url: Base URL of the threat-intel API.
        """
        self._api_key = threat_intel_api_key
        self._api_url = threat_intel_api_url

    def get_domain_age_days(self, domain: str) -> int | None:
        """Look up how many days ago a domain was registered.

        Args:
            domain: Registered domain, e.g. 'example.com'.

        Returns:
            Age in days, or None if WHOIS data is unavailable/unparseable.
        """
        try:
            record = whois.whois(domain)
        except Exception:  # WHOIS servers/libraries fail in many undocumented
            # ways (timeouts, rate limits, malformed registry responses,
            # or package-mix-up errors), so this is intentionally broad -
            # a lookup failure should degrade gracefully, not crash.
            logger.warning("WHOIS lookup failed for domain: %s", domain)
            return None

        creation_date = record.creation_date
        if isinstance(creation_date, list):
            creation_date = creation_date[0] if creation_date else None
        if creation_date is None:
            return None

        if creation_date.tzinfo is None:
            creation_date = creation_date.replace(tzinfo=timezone.utc)

        age = datetime.now(timezone.utc) - creation_date
        return age.days

    def is_recently_registered(self, domain: str) -> bool:
        """Flag domains registered within the suspicious recency window.

        Args:
            domain: Registered domain to check.

        Returns:
            True if age is below the threshold; False if older, or if the
            age is unknown (fail open: don't punish unresolvable WHOIS).
        """
        age_days = self.get_domain_age_days(domain)
        if age_days is None:
            return False
        return age_days < _NEW_DOMAIN_THRESHOLD_DAYS

    def check_threat_intel(self, domain: str) -> dict[str, float | bool | str]:
        """Query an external threat-intelligence API for a verdict.

        Args:
            domain: Registered domain to check.

        Returns:
            Dict with at least {'flagged': bool, 'score': float}. Returns a
            conservative default if the API call fails, so an outage
            degrades gracefully rather than blocking the whole pipeline.
        """
        try:
            response = requests.get(
                self._api_url,
                params={"domain": domain},
                headers={"Authorization": f"Bearer {self._api_key}"},
                timeout=_REQUEST_TIMEOUT_SECONDS,
            )
            response.raise_for_status()
        except requests.RequestException:
            logger.warning("Threat-intel API call failed for %s", domain)
            return {"flagged": False, "score": 0.0, "source": "unavailable"}

        payload = response.json()
        return {
            "flagged": bool(payload.get("flagged", False)),
            "score": float(payload.get("risk_score", 0.0)),
            "source": payload.get("provider", "unknown"),
        }
