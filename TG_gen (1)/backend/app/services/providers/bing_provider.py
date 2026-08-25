"""
Bing Visual Search Provider
============================
Uses the Bing Visual Search REST API to find visually similar products.

Requires: BING_VISUAL_SEARCH_API_KEY environment variable.
API docs: https://docs.microsoft.com/en-us/bing/search-apis/bing-visual-search/overview

No extra pip packages needed beyond httpx (already in requirements.txt).
"""
import logging
import re
from typing import List, Optional
from urllib.parse import urlparse

import httpx

from app.core.config import settings
from app.services.providers.google_vision_provider import (
    classify_domain, extract_fabric_text, _safe_domain
)
from app.services.providers.mock_provider import VisualMatchResult

logger = logging.getLogger(__name__)

_BING_ENDPOINT = "https://api.bing.microsoft.com/v7.0/images/visualsearch"


class BingVisualSearchProvider:
    """
    Calls the Bing Visual Search API with the uploaded image bytes.
    Falls back gracefully to an empty result list on any error.
    """

    def search(
        self,
        image_bytes: bytes,
        ai_predicted_fabric: Optional[str] = None,
        garment_category: Optional[str] = None,
        limit: int = 10,
    ) -> tuple[List[VisualMatchResult], List[str]]:
        """Returns (matches, related_entities)."""
        api_key = settings.BING_VISUAL_SEARCH_API_KEY
        if not api_key:
            logger.error("BING_VISUAL_SEARCH_API_KEY is not set.")
            return [], []

        try:
            headers = {
                "Ocp-Apim-Subscription-Key": api_key,
            }
            files = {
                "image": ("image.jpg", image_bytes, "image/jpeg"),
            }

            with httpx.Client(timeout=settings.VISUAL_SEARCH_TIMEOUT_SECONDS) as client:
                resp = client.post(_BING_ENDPOINT, headers=headers, files=files)

            if resp.status_code != 200:
                logger.error(
                    "Bing Visual Search returned HTTP %s: %s",
                    resp.status_code, resp.text[:200]
                )
                return [], []

            data = resp.json()
            results: List[VisualMatchResult] = []
            seen_urls: set = set()
            related_entities: List[str] = []

            tags = data.get("tags", [])
            for tag in tags:
                actions = tag.get("actions", [])
                for action in actions:
                    action_type = action.get("actionType", "")

                    # ── Pages containing the image ────────────────────────────
                    if action_type == "PagesIncluding":
                        for item in action.get("data", {}).get("value", []):
                            content_url = item.get("contentUrl", "")
                            host_page = item.get("hostPageUrl", content_url)

                            if not host_page or host_page in seen_urls:
                                continue
                            seen_urls.add(host_page)

                            domain = _safe_domain(host_page)
                            reliability = classify_domain(domain)

                            # Attempt fabric text extraction from name/description
                            snippet = item.get("name", "") + " " + item.get("description", "")
                            fabric_text = extract_fabric_text(snippet)

                            thumbnail = item.get("thumbnailUrl") or item.get("contentUrl")
                            price_info = item.get("offers", {})
                            price_text = None
                            if isinstance(price_info, dict):
                                price = price_info.get("price")
                                currency = price_info.get("priceCurrency", "")
                                if price:
                                    price_text = f"{currency}{price}"

                            score = max(0.5, 0.9 - len(results) * 0.03)

                            results.append(VisualMatchResult(
                                title=item.get("name") or domain,
                                source_url=host_page,
                                thumbnail_url=thumbnail,
                                source_domain=domain,
                                match_score=round(score, 3),
                                detected_product_type=action.get("displayName"),
                                fabric_text_found=fabric_text,
                                brand=item.get("brand", {}).get("name") if isinstance(item.get("brand"), dict) else None,
                                price_text=price_text,
                                source_reliability=reliability,
                                verification_status="source_text_found" if fabric_text else "not_verified",
                            ))

                            if len(results) >= limit:
                                break

                    # ── Related searches ──────────────────────────────────────
                    elif action_type == "RelatedSearches":
                        for term in action.get("data", {}).get("value", []):
                            text = term.get("text", "")
                            if text and text not in related_entities:
                                related_entities.append(text)

                if len(results) >= limit:
                    break

            if ai_predicted_fabric and ai_predicted_fabric not in related_entities:
                related_entities.insert(0, ai_predicted_fabric)

            return results[:limit], related_entities[:8]

        except httpx.TimeoutException:
            logger.error("Bing Visual Search request timed out after %ss", settings.VISUAL_SEARCH_TIMEOUT_SECONDS)
            return [], []
        except Exception as e:
            logger.error("Bing Visual Search failed: %s", e, exc_info=True)
            return [], []
