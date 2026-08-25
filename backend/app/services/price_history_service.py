"""
Price History Service
=====================
Manages recording and retrieval of historical price snapshots for fashion products.
"""
from __future__ import annotations

import datetime
import logging
from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.models import ProductPriceHistory
from app.schemas.outfit_schemas import PriceHistoryResponse, PriceSnapshot

logger = logging.getLogger(__name__)


class PriceHistoryService:

    @classmethod
    def record_snapshot(
        cls,
        db: Session,
        product_id: str,
        retailer: str,
        price_inr: float,
        original_price_inr: Optional[float] = None,
        is_verified: bool = True,
        source: str = "verified_feed",
    ) -> ProductPriceHistory:
        """Stores a price snapshot for a product."""
        snapshot = ProductPriceHistory(
            product_id=product_id,
            retailer=retailer,
            price_inr=price_inr,
            original_price_inr=original_price_inr,
            is_verified=is_verified,
            source=source,
            recorded_at=datetime.datetime.utcnow(),
        )
        db.add(snapshot)
        db.commit()
        db.refresh(snapshot)
        return snapshot

    @classmethod
    def get_price_history(
        cls,
        db: Session,
        product_id: str,
        current_price_inr: Optional[float] = None,
        retailer: Optional[str] = None,
    ) -> PriceHistoryResponse:
        """
        Retrieves historical price records, min, max, and current prices.
        """
        records = (
            db.query(ProductPriceHistory)
            .filter(ProductPriceHistory.product_id == product_id)
            .order_by(ProductPriceHistory.recorded_at.asc())
            .all()
        )

        if not records:
            # Check if we should provide a default initial snapshot if current price is given
            if current_price_inr is not None and current_price_inr > 0:
                cls.record_snapshot(
                    db=db,
                    product_id=product_id,
                    retailer=retailer or "Retailer",
                    price_inr=current_price_inr,
                    is_verified=True,
                )
                # Re-query
                records = (
                    db.query(ProductPriceHistory)
                    .filter(ProductPriceHistory.product_id == product_id)
                    .order_by(ProductPriceHistory.recorded_at.asc())
                    .all()
                )

        if not records:
            return PriceHistoryResponse(
                product_id=product_id,
                retailer=retailer,
                current_price_inr=current_price_inr,
                lowest_price_inr=current_price_inr,
                highest_price_inr=current_price_inr,
                snapshots=[],
                has_history=False,
                message="Price history will appear after we collect verified price updates.",
            )

        prices = [r.price_inr for r in records if r.price_inr is not None]
        lowest_price = min(prices) if prices else current_price_inr
        highest_price = max(prices) if prices else current_price_inr
        latest_price = records[-1].price_inr if records else current_price_inr
        latest_retailer = records[-1].retailer if records else retailer

        snapshots: List[PriceSnapshot] = [
            PriceSnapshot(
                price_inr=r.price_inr,
                original_price_inr=r.original_price_inr,
                is_verified=r.is_verified,
                recorded_at=r.recorded_at.isoformat(),
            )
            for r in records
        ]

        return PriceHistoryResponse(
            product_id=product_id,
            retailer=latest_retailer,
            current_price_inr=latest_price,
            lowest_price_inr=lowest_price,
            highest_price_inr=highest_price,
            snapshots=snapshots,
            has_history=len(snapshots) > 0,
            message="Verified price history available." if snapshots else "Price history will appear after we collect verified price updates.",
        )


_history_service: Optional[PriceHistoryService] = None

def get_price_history_service() -> PriceHistoryService:
    global _history_service
    if _history_service is None:
        _history_service = PriceHistoryService()
    return _history_service
