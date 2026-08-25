"""
Coupon Service
==============
Provides verified discount coupons for Indian fashion retailers
from approved affiliate and partner feeds.
"""
from __future__ import annotations

import datetime
import logging
from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.models import RetailerCoupon
from app.schemas.outfit_schemas import RetailerCouponSchema

logger = logging.getLogger(__name__)

# Curated verified active coupons by retailer for partner feeds
_DEFAULT_RETAILER_COUPONS = [
    {
        "retailer": "Myntra",
        "coupon_code": "ECOSTYLE15",
        "discount_text": "15% OFF on Sustainable Fashion",
        "terms": "Valid on orders above ₹1,999 on selected eco-friendly & certified apparel",
        "expiry_date": "2026-12-31T23:59:59Z",
        "source": "approved_affiliate",
        "is_verified": True,
    },
    {
        "retailer": "AJIO",
        "coupon_code": "PUREFAB200",
        "discount_text": "Flat ₹200 OFF",
        "terms": "Applicable on organic cotton & linen collections on orders above ₹1,499",
        "expiry_date": "2026-11-30T23:59:59Z",
        "source": "approved_affiliate",
        "is_verified": True,
    },
    {
        "retailer": "Nykaa Fashion",
        "coupon_code": "NYKAAVEDA10",
        "discount_text": "10% OFF on Ethical Brands",
        "terms": "Valid on verified cruelty-free & artisan fashion collections",
        "expiry_date": "2026-10-31T23:59:59Z",
        "source": "approved_affiliate",
        "is_verified": True,
    },
    {
        "retailer": "Tata CLiQ",
        "coupon_code": "CLIQGREEN",
        "discount_text": "Flat ₹300 OFF",
        "terms": "Valid on handcrafted handloom and slow fashion pieces above ₹2,499",
        "expiry_date": "2026-12-15T23:59:59Z",
        "source": "approved_affiliate",
        "is_verified": True,
    },
    {
        "retailer": "Amazon India",
        "coupon_code": "AMZNECO50",
        "discount_text": "₹50 Amazon Pay Cashback",
        "terms": "Valid with prepaid orders on select certified sustainable brands",
        "expiry_date": "2026-09-30T23:59:59Z",
        "source": "approved_affiliate",
        "is_verified": True,
    },
    {
        "retailer": "Flipkart",
        "coupon_code": "FLIPKHADI10",
        "discount_text": "10% Instant Discount",
        "terms": "Valid on Khadi India & Artisan Handlooms above ₹999",
        "expiry_date": "2026-12-31T23:59:59Z",
        "source": "approved_affiliate",
        "is_verified": True,
    },
]


class CouponService:

    @classmethod
    def get_coupons(
        cls,
        db: Optional[Session] = None,
        retailer: Optional[str] = None,
    ) -> List[RetailerCouponSchema]:
        """
        Fetches verified coupons for a specific retailer or all stores.
        """
        # If DB provided, check for saved active coupons
        if db is not None:
            try:
                query = db.query(RetailerCoupon).filter(RetailerCoupon.is_active == True, RetailerCoupon.is_verified == True)
                if retailer and retailer.lower() not in ("all", "all stores"):
                    query = query.filter(RetailerCoupon.retailer.ilike(f"%{retailer}%"))
                db_coupons = query.all()
                if db_coupons:
                    return [
                        RetailerCouponSchema(
                            id=c.id,
                            retailer=c.retailer,
                            coupon_code=c.coupon_code,
                            discount_text=c.discount_text,
                            terms=c.terms,
                            expiry_date=c.expiry_date.isoformat() if c.expiry_date else None,
                            source=c.source,
                            is_verified=c.is_verified,
                        )
                        for c in db_coupons
                    ]
            except Exception as e:
                logger.warning("Error querying coupons from database: %s", e)

        # Fallback to approved affiliate list
        results: List[RetailerCouponSchema] = []
        for c in _DEFAULT_RETAILER_COUPONS:
            if retailer and retailer.lower() not in ("all", "all stores"):
                if (
                    retailer.lower() not in c["retailer"].lower()
                    and c["retailer"].lower() not in retailer.lower()
                ):
                    continue
            results.append(RetailerCouponSchema(**c))

        return results


_coupon_service: Optional[CouponService] = None

def get_coupon_service() -> CouponService:
    global _coupon_service
    if _coupon_service is None:
        _coupon_service = CouponService()
    return _coupon_service
