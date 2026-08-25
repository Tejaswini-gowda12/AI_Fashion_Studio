"""
Product Normalizer Service
==========================
Normalizes raw retailer product data, validates URLs, calculates discount percentages,
and enforces the canonical ProductResult data model.
"""
from __future__ import annotations

import hashlib
import logging
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from app.schemas.outfit_schemas import ProductResult
from app.services.retailer_feed_adapter import is_safe_url

logger = logging.getLogger(__name__)


class ProductNormalizer:

    @staticmethod
    def generate_product_id(retailer: str, title: str, product_url: str) -> str:
        """Create a deterministic unique product ID based on retailer and URL/title."""
        raw_key = f"{retailer.lower().strip()}:{product_url.strip() or title.strip()}"
        return f"prod_{hashlib.md5(raw_key.encode('utf-8')).hexdigest()[:12]}"

    @classmethod
    def calculate_discount(
        cls,
        current_price: Optional[float],
        original_price: Optional[float],
    ) -> Optional[float]:
        """Calculates discount percentage if valid prices are provided."""
        if current_price is not None and original_price is not None:
            if original_price > current_price and original_price > 0:
                discount = ((original_price - current_price) / original_price) * 100.0
                return round(discount, 1)
        return None

    @classmethod
    def normalize(
        cls,
        raw_item: Dict[str, Any],
        outfit_item_name: str = "Outfit Item",
        default_status: str = "verified",
        default_source: str = "approved_affiliate_feed",
    ) -> Optional[ProductResult]:
        """
        Normalizes a raw product dict into canonical ProductResult.
        Rejects items with invalid or unsafe URLs.
        """
        retailer = (raw_item.get("retailer") or "Official Store").strip()
        title = (raw_item.get("title") or raw_item.get("name") or "Fashion Item").strip()
        product_url = (raw_item.get("product_url") or raw_item.get("url") or "").strip()
        image_url = raw_item.get("image_url")

        # URL Safety Check
        if not is_safe_url(product_url):
            logger.warning("Rejected unsafe product URL: %s", product_url)
            return None

        if image_url and not is_safe_url(image_url):
            image_url = None

        # Price normalization
        curr_price_raw = raw_item.get("current_price_inr") or raw_item.get("price_inr") or raw_item.get("price")
        current_price_inr: Optional[float] = None
        if curr_price_raw is not None:
            try:
                current_price_inr = float(curr_price_raw)
            except (ValueError, TypeError):
                current_price_inr = None

        orig_price_raw = raw_item.get("original_price_inr") or raw_item.get("mrp") or raw_item.get("original_price")
        original_price_inr: Optional[float] = None
        if orig_price_raw is not None:
            try:
                original_price_inr = float(orig_price_raw)
            except (ValueError, TypeError):
                original_price_inr = None

        discount_percent = raw_item.get("discount_percent")
        if discount_percent is None:
            discount_percent = cls.calculate_discount(current_price_inr, original_price_inr)
        else:
            try:
                discount_percent = round(float(discount_percent), 1)
            except (ValueError, TypeError):
                discount_percent = None

        # Match score (0.0 to 1.0)
        raw_score = raw_item.get("match_score", 0.85)
        try:
            match_score = max(0.0, min(1.0, float(raw_score)))
        except (ValueError, TypeError):
            match_score = 0.85

        product_id = raw_item.get("id") or cls.generate_product_id(retailer, title, product_url)
        status = raw_item.get("status") or default_status
        data_source = raw_item.get("data_source") or default_source

        # Timestamp
        last_updated_at = raw_item.get("last_updated_at") or raw_item.get("timestamp")
        if not last_updated_at:
            last_updated_at = datetime.now(timezone.utc).isoformat()

        fabric_details = raw_item.get("fabric_details")
        sustainability_details = raw_item.get("sustainability_details") or raw_item.get("sustainability_label")

        return ProductResult(
            id=str(product_id),
            outfit_item=outfit_item_name,
            title=title,
            retailer=retailer,
            product_url=product_url,
            image_url=image_url,
            current_price_inr=current_price_inr,
            original_price_inr=original_price_inr,
            discount_percent=discount_percent,
            fabric_details=fabric_details,
            sustainability_details=sustainability_details,
            match_score=match_score,
            data_source=data_source,
            status=status,
            last_updated_at=str(last_updated_at),
        )


_normalizer: Optional[ProductNormalizer] = None

def get_product_normalizer() -> ProductNormalizer:
    global _normalizer
    if _normalizer is None:
        _normalizer = ProductNormalizer()
    return _normalizer
