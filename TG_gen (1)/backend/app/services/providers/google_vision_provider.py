"""
Google Cloud Vision Web Detection Provider
==========================================
Uses the Google Cloud Vision API's WEB_DETECTION feature to find
pages containing visually similar images.

Authentication options (in priority order):
1. GOOGLE_APPLICATION_CREDENTIALS env var pointing to a service-account JSON file.
2. GOOGLE_VISION_API_KEY env var (simple API key — limited quota).

Requires: google-cloud-vision>=3.4.0
Install:  pip install google-cloud-vision
"""
import logging
import re
from typing import List, Optional
from urllib.parse import urlparse

from app.core.config import settings
from app.services.providers.mock_provider import VisualMatchResult

logger = logging.getLogger(__name__)

# ── Source reliability helpers ──────────────────────────────────────────────

_OFFICIAL_BRAND_DOMAINS = {
    "levi.com", "patagonia.com", "nike.com", "adidas.com", "gap.com",
    "uniqlo.com", "ralph-lauren.com", "tommyhilfiger.com", "calvinklein.com",
    "burberry.com", "gucci.com", "louisvuitton.com", "prada.com",
}
_RETAILER_DOMAINS = {
    "amazon.com", "amazon.co.uk", "nordstrom.com", "macys.com", "zappos.com",
    "asos.com", "hm.com", "zara.com", "shein.com", "shopify.com",
    "etsy.com", "ebay.com", "walmart.com", "target.com",
}
_EDITORIAL_DOMAINS = {
    "fashionrevolution.org", "textileexchange.org", "vogue.com", "gq.com", "elle.com",
    "treehugger.com", "goodonyou.eco", "ecocult.com",
}
_EDITORIAL_KEYWORDS = {"blog", "editorial", "magazine", "review", "guide", "news", "press", "journal", "article"}

# Fabric composition regex patterns (supporting optional adjectives like organic, recycled, combed, etc.)
_FABRIC_PATTERNS = [
    re.compile(
        r"(\d+)%\s*(?:organic\s+|recycled\s+|pure\s+|combed\s+|ring-spun\s+|post-consumer\s+)?(cotton|polyester|nylon|wool|silk|linen|hemp|viscose|rayon|elastane|spandex|acrylic|cashmere|denim|lyocell|tencel|bamboo)",
        re.I
    ),
    re.compile(
        r"(100%|pure)\s*(?:organic\s+|recycled\s+)?(cotton|wool|silk|linen|polyester|nylon|hemp|cashmere|denim|lyocell|viscose)",
        re.I
    ),
    re.compile(r"material[:\s]+([\w\s,%]+)", re.I),
    re.compile(r"fabric[:\s]+([\w\s,%]+)", re.I),
    re.compile(r"composition[:\s]+([\w\s,%]+)", re.I),
]


def classify_domain(domain: str) -> str:
    """Classify a domain as official_brand, retailer, blog_editorial, or unknown."""
    domain = domain.lower().lstrip("www.")
    if domain in _OFFICIAL_BRAND_DOMAINS:
        return "official_brand"
    if domain in _RETAILER_DOMAINS:
        return "retailer"
    if domain in _EDITORIAL_DOMAINS or any(kw in domain for kw in _EDITORIAL_KEYWORDS):
        return "blog_editorial"
    return "unknown"


def extract_fabric_text(snippet: str) -> Optional[str]:
    """
    Extract an explicit fabric composition statement from a page snippet.
    Returns None if no clear composition statement is found.
    Does NOT infer composition from visual similarity alone.
    """
    if not snippet:
        return None
    for pattern in _FABRIC_PATTERNS:
        m = pattern.search(snippet)
        if m:
            # Return the matched phrase (up to 120 chars)
            return snippet[m.start():m.end()][:120].strip()
    return None


def _safe_domain(url: str) -> str:
    """Extract the netloc from a URL, or return the raw string if parsing fails."""
    try:
        parsed = urlparse(url)
        return parsed.netloc.lstrip("www.")
    except Exception:
        return url[:50]


class GoogleVisionProvider:
    """
    Calls the Google Cloud Vision Web Detection API.
    Falls back gracefully to an empty result list on any API error.
    """

    def __init__(self):
        self._client = None

    def _get_client(self):
        if self._client is not None:
            return self._client

        try:
            from google.cloud import vision  # type: ignore
            import os

            api_key = settings.GOOGLE_VISION_API_KEY or ""

            if api_key:
                # Simple API key auth (limited)
                from google.api_core.gapic_v1 import client_info
                self._client = vision.ImageAnnotatorClient(
                    client_options={"api_key": api_key}
                )
            else:
                # Service account (GOOGLE_APPLICATION_CREDENTIALS env var)
                self._client = vision.ImageAnnotatorClient()

            return self._client
        except ImportError:
            logger.error(
                "google-cloud-vision is not installed. "
                "Run: pip install google-cloud-vision"
            )
            raise
        except Exception as e:
            logger.error("Failed to initialise Google Vision client: %s", e)
            raise

    def search(
        self,
        image_bytes: bytes,
        ai_predicted_fabric: Optional[str] = None,
        garment_category: Optional[str] = None,
        limit: int = 10,
    ) -> tuple[List[VisualMatchResult], List[str]]:
        """Returns (matches, related_entities)."""
        try:
            from google.cloud import vision  # type: ignore
            client = self._get_client()

            image = vision.Image(content=image_bytes)
            features = [vision.Feature(type_=vision.Feature.Type.WEB_DETECTION)]

            request = vision.AnnotateImageRequest(image=image, features=features)
            response = client.annotate_image(request=request)

            if response.error.message:
                logger.error("Google Vision API error: %s", response.error.message)
                return [], []

            web = response.web_detection
            results: List[VisualMatchResult] = []
            seen_urls: set = set()

            # Pages with matching images (ranked by Google)
            for page in web.pages_with_matching_images[:limit]:
                url = page.url
                if not url or url in seen_urls:
                    continue
                seen_urls.add(url)

                domain = _safe_domain(url)
                reliability = classify_domain(domain)

                # Try to extract fabric text from page snippets
                snippet = page.page_title or ""
                fabric_text = extract_fabric_text(snippet)

                # Use first partial/full matching image as thumbnail
                thumbnail = None
                if page.partial_matching_images:
                    thumbnail = page.partial_matching_images[0].url
                elif page.full_matching_images:
                    thumbnail = page.full_matching_images[0].url

                # Score: Google ranks them but doesn't give a numeric score; we synthesise one
                score = max(0.5, 0.95 - len(results) * 0.04)

                results.append(VisualMatchResult(
                    title=page.page_title or domain,
                    source_url=url,
                    thumbnail_url=thumbnail,
                    source_domain=domain,
                    match_score=round(score, 3),
                    fabric_text_found=fabric_text,
                    source_reliability=reliability,
                    verification_status="source_text_found" if fabric_text else "not_verified",
                ))

            # Related entities from web entities
            related_entities = [e.description for e in web.web_entities[:8] if e.description]
            if ai_predicted_fabric and ai_predicted_fabric not in related_entities:
                related_entities.insert(0, ai_predicted_fabric)

            return results[:limit], related_entities

        except Exception as e:
            logger.error("Google Vision Web Detection failed: %s", e, exc_info=True)
            return [], []
