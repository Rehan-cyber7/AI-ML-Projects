"""Screenshot capture and perceptual-hash comparison for visual phishing
detection.

Captures a page render either via local Selenium (headless Chromium) or a
hosted screenshot API, then compares it against known brand-page hashes.
This layer is optional and slower than the others - see README.md for how
to enable it and keep it out of the synchronous request path.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from io import BytesIO

import imagehash
import requests
from PIL import Image
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

logger = logging.getLogger(__name__)

_SCREENSHOT_TIMEOUT_SECONDS = 15
_SIMILARITY_HAMMING_THRESHOLD = 10  # Lower = more visually similar.


@dataclass(frozen=True)
class BrandTemplate:
    """A known-legitimate page's visual fingerprint for comparison."""

    brand_name: str
    legitimate_domain: str
    reference_hash: imagehash.ImageHash


class ScreenshotAnalyzer:
    """Captures and compares page screenshots against known brand templates."""

    def __init__(self, brand_templates: list[BrandTemplate]) -> None:
        """Configure the analyzer with a reference set of brand templates.

        Args:
            brand_templates: Pre-computed pHashes of pages worth protecting
                (e.g. your own login page, or frequently-impersonated
                brands relevant to your user base).
        """
        self._templates = brand_templates

    def capture_via_selenium(self, url: str) -> Image.Image:
        """Render a URL headlessly and return the screenshot as a PIL Image.

        Args:
            url: Fully-qualified URL to render.

        Returns:
            Screenshot as a PIL Image.

        Raises:
            RuntimeError: If the page fails to load within the timeout.
        """
        options = Options()
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1280,800")

        driver = webdriver.Chrome(options=options)
        try:
            driver.set_page_load_timeout(_SCREENSHOT_TIMEOUT_SECONDS)
            driver.get(url)
            png_bytes = driver.get_screenshot_as_png()
        except Exception as exc:  # Selenium raises several distinct types.
            raise RuntimeError(f"Failed to capture screenshot for {url}") from exc
        finally:
            driver.quit()

        return Image.open(BytesIO(png_bytes))

    def capture_via_api(self, url: str, api_key: str, api_url: str) -> Image.Image:
        """Alternative to Selenium: use a hosted screenshot API service.

        Useful in environments where running a headless browser is
        impractical (e.g. constrained serverless deployments).

        Args:
            url: Fully-qualified URL to render.
            api_key: API key for the screenshot service, e.g. [YOUR_API_KEY].
            api_url: Base endpoint of the screenshot service.

        Returns:
            Screenshot as a PIL Image.

        Raises:
            requests.RequestException: If the API call fails.
        """
        response = requests.get(
            api_url,
            params={"url": url, "key": api_key, "format": "png"},
            timeout=_SCREENSHOT_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        return Image.open(BytesIO(response.content))

    def find_closest_brand_match(
        self, screenshot: Image.Image
    ) -> tuple[BrandTemplate | None, int]:
        """Find the most visually similar known brand template, if any.

        Args:
            screenshot: The captured page screenshot.

        Returns:
            Tuple of (best-matching BrandTemplate or None, Hamming distance).
            Returns (None, -1) if no template is within the similarity
            threshold.
        """
        candidate_hash = imagehash.phash(screenshot)

        best_template: BrandTemplate | None = None
        best_distance = _SIMILARITY_HAMMING_THRESHOLD + 1

        for template in self._templates:
            distance = candidate_hash - template.reference_hash
            if distance < best_distance:
                best_template, best_distance = template, distance

        if best_distance <= _SIMILARITY_HAMMING_THRESHOLD:
            return best_template, best_distance
        return None, -1

    def analyze(self, url: str, domain: str) -> dict[str, str | int | bool | None]:
        """Run the full visual analysis pipeline for a URL.

        Args:
            url: Fully-qualified URL to analyze.
            domain: The registered domain the URL is currently served from.

        Returns:
            Dict describing whether a brand-impersonation mismatch was
            detected.
        """
        screenshot = self.capture_via_selenium(url)
        match, distance = self.find_closest_brand_match(screenshot)

        if match is None:
            return {"brand_match": None, "hosted_on_legitimate_domain": True}

        return {
            "brand_match": match.brand_name,
            "hosted_on_legitimate_domain": domain == match.legitimate_domain,
            "hamming_distance": distance,
        }
