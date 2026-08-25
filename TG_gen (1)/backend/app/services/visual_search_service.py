"""
Visual Search Service
======================
Abstraction layer over multiple visual-search API providers.

Provider selection is controlled by the VISUAL_SEARCH_PROVIDER environment variable:
  - "mock"          → MockVisualSearchProvider  (default, no API key needed)
  - "google_vision" → GoogleVisionProvider      (requires GOOGLE_VISION_API_KEY or GOOGLE_APPLICATION_CREDENTIALS)
  - "bing"          → BingVisualSearchProvider  (requires BING_VISUAL_SEARCH_API_KEY)

If the configured provider fails initialisation, the service automatically
falls back to the mock provider so the application stays functional.
"""
import logging
from typing import List, Optional
from urllib.parse import urlparse

from app.core.config import settings
from app.services.providers.mock_provider import MockVisualSearchProvider, VisualMatchResult

logger = logging.getLogger(__name__)


def _is_safe_url(url: str) -> bool:
    """
    Validate that a URL returned by the provider is safe to expose to clients.
    Rejects non-http(s) schemes and overly long URLs.
    """
    try:
        parsed = urlparse(url)
        return parsed.scheme in ("http", "https") and bool(parsed.netloc) and len(url) < 2048
    except Exception:
        return False


def _deduplicate(matches: List[VisualMatchResult]) -> List[VisualMatchResult]:
    """Remove duplicate source URLs, keeping the highest-scored entry."""
    seen: dict[str, VisualMatchResult] = {}
    for m in matches:
        existing = seen.get(m.source_url)
        if existing is None or m.match_score > existing.match_score:
            seen[m.source_url] = m
    # Re-sort by score descending
    return sorted(seen.values(), key=lambda r: r.match_score, reverse=True)


class VisualSearchService:
    """
    Main service class.  Call `search()` to run a visual web search.
    The underlying provider is selected once at startup via `get_visual_search_service()`.
    """

    def __init__(self, provider, provider_name: str):
        self._provider = provider
        self._provider_name = provider_name

    @property
    def provider_name(self) -> str:
        return self._provider_name

    def search(
        self,
        image_bytes: bytes,
        ai_predicted_fabric: Optional[str] = None,
        garment_category: Optional[str] = None,
        limit: int = 10,
    ) -> dict:
        """
        Run a visual search and return a structured result dict.

        Returns:
        {
            "search_status": "success" | "no_results" | "failed",
            "provider_used": str,
            "matches": List[VisualMatchResult],
            "related_entities": List[str],
            "query_context": {"ai_predicted_fabric": str|None, "garment_type": str|None},
        }
        """
        effective_limit = min(limit, settings.VISUAL_SEARCH_RESULT_LIMIT)

        try:
            raw_matches, related_entities = self._provider.search(
                image_bytes=image_bytes,
                ai_predicted_fabric=ai_predicted_fabric,
                garment_category=garment_category,
                limit=effective_limit * 2,  # over-fetch then deduplicate
            )
        except Exception as e:
            logger.error("VisualSearchService: provider raised unexpectedly: %s", e, exc_info=True)
            raw_matches, related_entities = [], []

        # ── Post-processing pipeline ──────────────────────────────────────────

        # 1. Filter unsafe URLs
        safe_matches = [m for m in raw_matches if _is_safe_url(m.source_url)]

        # 2. Deduplicate by URL
        deduped = _deduplicate(safe_matches)

        # 3. Truncate to the requested limit
        final_matches = deduped[:effective_limit]

        status = "success" if final_matches else "no_results"

        return {
            "search_status": status,
            "provider_used": self._provider_name,
            "matches": final_matches,
            "related_entities": related_entities,
            "query_context": {
                "ai_predicted_fabric": ai_predicted_fabric,
                "garment_type": garment_category,
            },
        }


# ── Singleton factory ─────────────────────────────────────────────────────────

_service_instance: Optional[VisualSearchService] = None


def get_visual_search_service() -> VisualSearchService:
    """
    Returns a singleton VisualSearchService configured from env vars.
    Falls back to mock if the requested provider cannot be initialised.
    """
    global _service_instance
    if _service_instance is not None:
        return _service_instance

    provider_name = settings.VISUAL_SEARCH_PROVIDER.lower()
    logger.info("Initialising VisualSearchService with provider: %s", provider_name)

    provider = None

    if provider_name == "google_vision":
        try:
            from app.services.providers.google_vision_provider import GoogleVisionProvider
            provider = GoogleVisionProvider()
            # Validate the client can be created (catches missing credentials early)
            provider._get_client()
            logger.info("Google Vision Web Detection provider ready.")
        except Exception as e:
            logger.warning(
                "Could not initialise GoogleVisionProvider (%s). Falling back to mock.", e
            )
            provider = None
            provider_name = "mock"

    elif provider_name == "bing":
        if not settings.BING_VISUAL_SEARCH_API_KEY:
            logger.warning("BING_VISUAL_SEARCH_API_KEY is not set. Falling back to mock.")
            provider_name = "mock"
        else:
            from app.services.providers.bing_provider import BingVisualSearchProvider
            provider = BingVisualSearchProvider()
            logger.info("Bing Visual Search provider ready.")

    if provider is None:
        provider = MockVisualSearchProvider()
        provider_name = "mock"
        logger.info("Using Mock Visual Search provider (demo mode).")

    _service_instance = VisualSearchService(provider=provider, provider_name=provider_name)
    return _service_instance
