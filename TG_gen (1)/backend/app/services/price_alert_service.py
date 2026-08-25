"""
Price Alert Service
===================
Manages price alert subscriptions for saved products and checks triggers when
verified prices update.
"""
from __future__ import annotations

import datetime
import logging
from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.models import PriceAlert
from app.schemas.outfit_schemas import PriceAlertCreateRequest, PriceAlertResponse

logger = logging.getLogger(__name__)


class PriceAlertService:

    @classmethod
    def create_price_alert(
        cls,
        db: Session,
        payload: PriceAlertCreateRequest,
        user_id: Optional[int] = None,
    ) -> PriceAlertResponse:
        """
        Subscribes a user to a price alert for a target product price.
        """
        # Check if existing alert exists for this user and product
        existing = (
            db.query(PriceAlert)
            .filter(
                PriceAlert.product_id == payload.product_id,
                PriceAlert.user_id == user_id,
                PriceAlert.is_active == True,
            )
            .first()
        )

        if existing:
            existing.target_price_inr = payload.target_price_inr
            existing.current_price_inr = payload.current_price_inr
            db.commit()
            db.refresh(existing)
            return PriceAlertResponse(
                id=existing.id,
                product_id=existing.product_id,
                product_title=existing.product_title,
                retailer=existing.retailer,
                target_price_inr=existing.target_price_inr,
                current_price_inr=existing.current_price_inr,
                is_active=existing.is_active,
                is_triggered=existing.is_triggered,
                created_at=existing.created_at,
                message="Existing price alert updated to new target price.",
            )

        alert = PriceAlert(
            user_id=user_id,
            product_id=payload.product_id,
            product_title=payload.product_title,
            product_url=payload.product_url,
            retailer=payload.retailer,
            target_price_inr=payload.target_price_inr,
            initial_price_inr=payload.initial_price_inr or payload.current_price_inr,
            current_price_inr=payload.current_price_inr,
            is_active=True,
            is_triggered=False,
            created_at=datetime.datetime.utcnow(),
        )
        db.add(alert)
        db.commit()
        db.refresh(alert)

        return PriceAlertResponse(
            id=alert.id,
            product_id=alert.product_id,
            product_title=alert.product_title,
            retailer=alert.retailer,
            target_price_inr=alert.target_price_inr,
            current_price_inr=alert.current_price_inr,
            is_active=alert.is_active,
            is_triggered=alert.is_triggered,
            created_at=alert.created_at,
            message="Price alert configured successfully! You will be notified when the price reaches your target.",
        )

    @classmethod
    def check_and_trigger_alerts(
        cls,
        db: Session,
        product_id: str,
        fresh_price_inr: float,
    ) -> List[PriceAlert]:
        """
        Evaluates active alerts for a product against a fresh verified price update.
        """
        active_alerts = (
            db.query(PriceAlert)
            .filter(
                PriceAlert.product_id == product_id,
                PriceAlert.is_active == True,
                PriceAlert.is_triggered == False,
            )
            .all()
        )

        triggered_list: List[PriceAlert] = []
        for alert in active_alerts:
            alert.current_price_inr = fresh_price_inr
            if fresh_price_inr <= alert.target_price_inr:
                alert.is_triggered = True
                alert.triggered_at = datetime.datetime.utcnow()
                triggered_list.append(alert)
                logger.info(
                    "Price alert #%s triggered! Target: ₹%s, Current: ₹%s",
                    alert.id,
                    alert.target_price_inr,
                    fresh_price_inr,
                )

        if active_alerts:
            db.commit()

        return triggered_list


_alert_service: Optional[PriceAlertService] = None

def get_price_alert_service() -> PriceAlertService:
    global _alert_service
    if _alert_service is None:
        _alert_service = PriceAlertService()
    return _alert_service
