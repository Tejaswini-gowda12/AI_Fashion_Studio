"""
AI Outfit Studio – Compare Prices & Buy Similar Styles Endpoints
=================================================================
POST /api/outfit-studio/products/search         – Search products for outfit items
GET  /api/outfit-studio/products/compare        – Compare prices across Indian retailers
POST /api/outfit-studio/products/save           – Save a product to user favorites (auth optional/supported)
POST /api/outfit-studio/price-alerts            – Create a price alert target
GET  /api/outfit-studio/products/{id}/price-history – Get price history and min/max/current stats
GET  /api/outfit-studio/coupons                 – Get verified coupons from approved partners
"""
from __future__ import annotations

import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.v1.dependencies import get_current_user_optional, get_db
from app.models.models import SavedProduct, User
from app.schemas.outfit_schemas import (
    PriceAlertCreateRequest,
    PriceAlertResponse,
    PriceComparisonResponse,
    PriceHistoryResponse,
    ProductResult,
    ProductSaveRequest,
    ProductSaveResponse,
    ProductSearchRequest,
    RetailerCouponSchema,
)
from app.services.coupon_service import get_coupon_service
from app.services.price_alert_service import get_price_alert_service
from app.services.price_history_service import get_price_history_service
from app.services.product_search_service import get_product_search_service

logger = logging.getLogger(__name__)
router = APIRouter()


# ─────────────────────────────────────────────────────────────────────────────
# 1. Product Search
# ─────────────────────────────────────────────────────────────────────────────
@router.post(
    "/products/search",
    response_model=PriceComparisonResponse,
    summary="Search real fashion products from Indian stores for generated outfit items",
    tags=["Outfit Studio - Shopping & Comparison"],
)
def search_products(
    payload: ProductSearchRequest,
    db: Session = Depends(get_db),
):
    """
    Finds matching real fashion items across Myntra, AJIO, Nykaa Fashion,
    Tata CLiQ, Amazon India, Flipkart, and Official Brands.
    """
    service = get_product_search_service()
    try:
        return service.search_and_compare(request=payload, db=db)
    except Exception as e:
        logger.error("Product search failed: %s", e, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Product search failed: {e}",
        )


# ─────────────────────────────────────────────────────────────────────────────
# 2. Product Comparison (GET)
# ─────────────────────────────────────────────────────────────────────────────
@router.get(
    "/products/compare",
    response_model=PriceComparisonResponse,
    summary="Compare prices and discover similar styles for an outfit item",
    tags=["Outfit Studio - Shopping & Comparison"],
)
def compare_products(
    outfit_item_name: Optional[str] = Query(None, description="Name of the outfit garment"),
    category: Optional[str] = Query(None, description="Category, e.g. Dress, Top, Footwear"),
    gender: Optional[str] = Query(None, description="women | men | unisex"),
    style: Optional[str] = Query(None, description="casual | formal | traditional | party"),
    color: Optional[str] = Query(None, description="Color preference"),
    fabric: Optional[str] = Query(None, description="Fabric preference"),
    occasion: Optional[str] = Query(None, description="Occasion"),
    budget_inr: Optional[float] = Query(None, description="Max budget in INR"),
    retailer_filter: Optional[str] = Query("All Stores", description="Filter by store"),
    limit: int = Query(12, ge=1, le=50),
    db: Session = Depends(get_db),
):
    """
    Returns price comparison data, Best Price card, Best Sustainable Option,
    and retailer fallback links.
    """
    service = get_product_search_service()
    request = ProductSearchRequest(
        outfit_item_name=outfit_item_name or "Fashion Item",
        category=category,
        gender=gender,
        style=style,
        color=color,
        fabric=fabric,
        occasion=occasion,
        budget_inr=budget_inr,
        retailer_filter=retailer_filter,
        limit=limit,
    )
    return service.search_and_compare(request=request, db=db)


# ─────────────────────────────────────────────────────────────────────────────
# 3. Save Product
# ─────────────────────────────────────────────────────────────────────────────
@router.post(
    "/products/save",
    response_model=ProductSaveResponse,
    summary="Save a verified product to user profile / wishlist",
    tags=["Outfit Studio - Shopping & Comparison"],
)
def save_product(
    payload: ProductSaveRequest,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    """
    Saves a matched fashion product to the user's saved wishlist.
    """
    prod = payload.product
    saved = SavedProduct(
        user_id=current_user.id if current_user else None,
        product_id=prod.id,
        outfit_item=prod.outfit_item,
        title=prod.title,
        retailer=prod.retailer,
        product_url=prod.product_url,
        image_url=prod.image_url,
        current_price_inr=prod.current_price_inr,
        original_price_inr=prod.original_price_inr,
        discount_percent=prod.discount_percent,
        fabric_details=prod.fabric_details,
        sustainability_details=prod.sustainability_details,
        match_score=prod.match_score,
        data_source=prod.data_source,
        status=prod.status,
    )
    db.add(saved)
    db.commit()
    db.refresh(saved)

    # Also record initial price snapshot in history table
    if prod.current_price_inr:
        history_svc = get_price_history_service()
        history_svc.record_snapshot(
            db=db,
            product_id=prod.id,
            retailer=prod.retailer,
            price_inr=prod.current_price_inr,
            original_price_inr=prod.original_price_inr,
            is_verified=(prod.status == "verified"),
        )

    return ProductSaveResponse(
        id=saved.id,
        product_id=saved.product_id,
        title=saved.title,
        retailer=saved.retailer,
        saved_at=saved.saved_at,
        message="Product saved to your profile.",
    )


# ─────────────────────────────────────────────────────────────────────────────
# 4. Set Price Alert
# ─────────────────────────────────────────────────────────────────────────────
@router.post(
    "/price-alerts",
    response_model=PriceAlertResponse,
    summary="Create or update a price drop alert for a product",
    tags=["Outfit Studio - Shopping & Comparison"],
)
def create_price_alert(
    payload: PriceAlertCreateRequest,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    """
    Configures a target price alert in INR for a verified product.
    """
    service = get_price_alert_service()
    return service.create_price_alert(
        db=db,
        payload=payload,
        user_id=current_user.id if current_user else None,
    )


# ─────────────────────────────────────────────────────────────────────────────
# 5. Price History
# ─────────────────────────────────────────────────────────────────────────────
@router.get(
    "/products/{product_id}/price-history",
    response_model=PriceHistoryResponse,
    summary="Get historical price snapshots and trends for a product",
    tags=["Outfit Studio - Shopping & Comparison"],
)
def get_product_price_history(
    product_id: str,
    current_price_inr: Optional[float] = Query(None, description="Current price in INR"),
    retailer: Optional[str] = Query(None, description="Retailer name"),
    db: Session = Depends(get_db),
):
    """
    Returns timeline of verified price points, minimum, maximum, and current price.
    """
    service = get_price_history_service()
    return service.get_price_history(
        db=db,
        product_id=product_id,
        current_price_inr=current_price_inr,
        retailer=retailer,
    )


# ─────────────────────────────────────────────────────────────────────────────
# 6. Verified Coupons
# ─────────────────────────────────────────────────────────────────────────────
@router.get(
    "/coupons",
    response_model=List[RetailerCouponSchema],
    summary="Get verified promotional coupons for Indian retailers",
    tags=["Outfit Studio - Shopping & Comparison"],
)
def get_retailer_coupons(
    retailer: Optional[str] = Query(None, description="Filter coupons by retailer"),
    db: Session = Depends(get_db),
):
    """
    Returns active verified coupons supplied by approved affiliate / partner feeds.
    """
    service = get_coupon_service()
    return service.get_coupons(db=db, retailer=retailer)
