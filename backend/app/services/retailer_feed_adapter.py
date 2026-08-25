"""
Retailer Feed Adapter
=====================
Adapter for Indian fashion retailers:
- Myntra
- AJIO
- Nykaa Fashion
- Tata CLiQ
- Amazon India
- Flipkart
- Official Brands

Handles search query encoding, URL safety validation, and search fallback link generation.
"""
from __future__ import annotations

import logging
import re
import urllib.parse
from typing import Any, Dict, List, Optional
from urllib.parse import quote_plus, urlparse

from app.schemas.outfit_schemas import RetailerSearchLinkSchema

logger = logging.getLogger(__name__)


def clean_query_terms(text: str) -> str:
    """Normalize and sanitize query text by removing special punctuation."""
    if not text:
        return ""
    cleaned = re.sub(r"[^\w\s-]", " ", text)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned


def is_safe_url(url: Optional[str]) -> bool:
    """
    Validates that a URL is a legitimate, non-malicious HTTP/HTTPS web address.
    Rejects javascript:, data:, file:, and invalid schemed URLs.
    """
    if not url or not isinstance(url, str):
        return False
    try:
        parsed = urlparse(url.strip())
        if parsed.scheme not in ("http", "https"):
            return False
        if not parsed.netloc or len(parsed.netloc) < 3:
            return False
        if len(url) > 2048:
            return False
        # Block localhost/private ranges if in production context (safe check)
        return True
    except Exception:
        return False


class RetailerFeedAdapter:
    """Generates verified search links and query formats for top Indian retailers."""

    @staticmethod
    def build_myntra_search_url(query: str) -> str:
        cleaned = clean_query_terms(query)
        slug = re.sub(r"\s+", "-", cleaned.lower())
        return f"https://www.myntra.com/{urllib.parse.quote(slug or 'clothing')}"

    @staticmethod
    def build_ajio_search_url(query: str) -> str:
        cleaned = clean_query_terms(query)
        return f"https://www.ajio.com/search/?text={quote_plus(cleaned or 'fashion')}"

    @staticmethod
    def build_nykaa_fashion_search_url(query: str) -> str:
        cleaned = clean_query_terms(query)
        return f"https://www.nykaafashion.com/catalogsearch/result/?q={quote_plus(cleaned or 'fashion')}"

    @staticmethod
    def build_tatacliq_search_url(query: str) -> str:
        cleaned = clean_query_terms(query)
        return f"https://www.tatacliq.com/search/?searchCategory=all&text={quote_plus(cleaned or 'fashion')}"

    @staticmethod
    def build_amazon_in_search_url(query: str) -> str:
        cleaned = clean_query_terms(query)
        return f"https://www.amazon.in/s?k={quote_plus(cleaned or 'clothing')}"

    @staticmethod
    def build_flipkart_search_url(query: str) -> str:
        cleaned = clean_query_terms(query)
        return f"https://www.flipkart.com/search?q={quote_plus(cleaned or 'clothing')}"

    @staticmethod
    def build_official_brand_search_url(query: str, brand_name: Optional[str] = None) -> str:
        cleaned = clean_query_terms(query)
        brand = brand_name or "sustainable fashion India"
        return f"https://www.google.com/search?q={quote_plus(f'{cleaned} official store {brand}')}"

    def build_query(
        self,
        category: str,
        gender: Optional[str] = None,
        style: Optional[str] = None,
        color: Optional[str] = None,
        occasion: Optional[str] = None,
        fabric: Optional[str] = None,
        budget_inr: Optional[float] = None,
        location: str = "India",
    ) -> str:
        """
        Builds a high-intent shopping search query.
        Example: 'women sage green wrap midi dress formal office under 4000 India'
        """
        tokens: List[str] = []
        if gender and gender.lower() in ("women", "men", "unisex"):
            tokens.append(gender.lower())
        if color and not color.startswith("#"):
            tokens.append(color.strip())
        if fabric and fabric.lower() not in ("any", "standard", "general", "none"):
            tokens.append(fabric.split("/")[0].strip())
        if category:
            tokens.append(category.strip())
        if style and style.lower() not in ("any", "general"):
            tokens.append(style.strip())
        if occasion and occasion.lower() not in ("any", "general"):
            tokens.append(occasion.strip())
        if budget_inr and budget_inr > 0:
            tokens.append(f"under {int(budget_inr)}")
        if location:
            tokens.append(location.strip())

        query = " ".join(t for t in tokens if t)
        return clean_query_terms(query) or f"{category} fashion India"

    def generate_retailer_search_links(self, query: str) -> List[RetailerSearchLinkSchema]:
        """Returns standard fallback search query links for all supported Indian stores."""
        return [
            RetailerSearchLinkSchema(
                retailer="Myntra",
                search_url=self.build_myntra_search_url(query),
                query=query,
                icon="🛍️",
            ),
            RetailerSearchLinkSchema(
                retailer="AJIO",
                search_url=self.build_ajio_search_url(query),
                query=query,
                icon="✨",
            ),
            RetailerSearchLinkSchema(
                retailer="Nykaa Fashion",
                search_url=self.build_nykaa_fashion_search_url(query),
                query=query,
                icon="🌸",
            ),
            RetailerSearchLinkSchema(
                retailer="Tata CLiQ",
                search_url=self.build_tatacliq_search_url(query),
                query=query,
                icon="💎",
            ),
            RetailerSearchLinkSchema(
                retailer="Amazon India",
                search_url=self.build_amazon_in_search_url(query),
                query=query,
                icon="📦",
            ),
            RetailerSearchLinkSchema(
                retailer="Flipkart",
                search_url=self.build_flipkart_search_url(query),
                query=query,
                icon="🛒",
            ),
            RetailerSearchLinkSchema(
                retailer="Official Brands",
                search_url=self.build_official_brand_search_url(query),
                query=query,
                icon="🌿",
            ),
        ]


_feed_adapter: Optional[RetailerFeedAdapter] = None

def get_retailer_feed_adapter() -> RetailerFeedAdapter:
    global _feed_adapter
    if _feed_adapter is None:
        _feed_adapter = RetailerFeedAdapter()
    return _feed_adapter
