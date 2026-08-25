"""
Price Comparison Service
========================
Calculates the best price product, best sustainable option, and computes
estimated savings against the next cheapest matching product from verified sources.
"""
from __future__ import annotations

import logging
from typing import List, Optional

from app.schemas.outfit_schemas import BestDealInfo, ProductResult

logger = logging.getLogger(__name__)


class PriceComparisonService:

    @classmethod
    def find_best_deal(cls, products: List[ProductResult]) -> Optional[BestDealInfo]:
        """
        Computes Best Price product, Best Sustainable product, and estimated savings.
        """
        if not products:
            return None

        # Filter products with valid price
        priced_products = [p for p in products if p.current_price_inr is not None and p.current_price_inr > 0]
        if not priced_products:
            return None

        # Sort priced products ascending
        sorted_by_price = sorted(priced_products, key=lambda x: x.current_price_inr)
        best_price_prod = sorted_by_price[0]

        # Best sustainable product (looks for sustainability details/keywords or eco certified)
        sustainable_candidates = [
            p for p in priced_products
            if p.sustainability_details or any(
                term in (p.fabric_details or "").lower() or term in p.title.lower()
                for term in ("organic", "tencel", "lyocell", "linen", "bamboo", "hemp", "recycled", "khadi", "gots", "vegan")
            )
        ]
        best_sustainable_prod = sustainable_candidates[0] if sustainable_candidates else None

        # Calculate estimated savings against the next cheapest product
        estimated_savings: Optional[float] = None
        next_cheapest_price: Optional[float] = None
        has_verified_savings = False

        if len(sorted_by_price) > 1:
            next_cheapest = sorted_by_price[1]
            diff = next_cheapest.current_price_inr - best_price_prod.current_price_inr
            if diff > 0:
                estimated_savings = round(diff, 2)
                next_cheapest_price = next_cheapest.current_price_inr

                # Rule: Only mark as verified savings when prices come from verified source
                if best_price_prod.status == "verified" and next_cheapest.status == "verified":
                    has_verified_savings = True

        is_verified_feed = all(p.status == "verified" for p in priced_products[:2])
        source_label = "Verified Live Feed" if is_verified_feed else "Sample Comparison Catalog"

        return BestDealInfo(
            best_price_product=best_price_prod,
            best_sustainable_product=best_sustainable_prod or best_price_prod,
            estimated_savings_inr=estimated_savings,
            next_cheapest_price_inr=next_cheapest_price,
            verified_source_label=source_label,
            has_verified_savings=has_verified_savings,
        )


_comparison_service: Optional[PriceComparisonService] = None

def get_price_comparison_service() -> PriceComparisonService:
    global _comparison_service
    if _comparison_service is None:
        _comparison_service = PriceComparisonService()
    return _comparison_service
