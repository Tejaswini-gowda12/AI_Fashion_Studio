"""
Tests for AI Outfit Studio – Compare Prices & Buy Similar Styles Feature
========================================================================
Covers:
- Product matching & attribute scoring from outfit items
- Duplicate product removal & canonical URL deduplication
- Best-price & estimated savings calculation
- URL safety validator rejecting invalid/malicious URLs
- Retailer search fallback buttons for top Indian stores
- Demo vs Verified mode labelling
- Price alert creation & trigger evaluation
- Price history snapshot recording & statistics
- Verified coupon service
- FastAPI comparison and shopping endpoints
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.db.database import get_db, Base, engine
from app.models.models import SavedProduct, PriceAlert, ProductPriceHistory, RetailerCoupon
from app.schemas.outfit_schemas import ProductResult, ProductSearchRequest, PriceAlertCreateRequest
from app.services.retailer_feed_adapter import RetailerFeedAdapter, is_safe_url, clean_query_terms
from app.services.product_normalizer import ProductNormalizer
from app.services.product_match_service import ProductMatchService
from app.services.price_comparison_service import PriceComparisonService
from app.services.price_alert_service import PriceAlertService
from app.services.price_history_service import PriceHistoryService
from app.services.coupon_service import CouponService
from app.services.product_search_service import ProductSearchService

client = TestClient(app)


# ─────────────────────────────────────────────────────────────────────────────
# 1. URL Safety & Retailer Adapter Tests
# ─────────────────────────────────────────────────────────────────────────────

def test_url_safety_validation():
    """Verifies that only valid HTTP/HTTPS URLs are allowed and malicious schemes rejected."""
    assert is_safe_url("https://www.myntra.com/dresses") is True
    assert is_safe_url("http://www.ajio.com/search/?text=linen") is True
    assert is_safe_url("https://www.nykaafashion.com/item/123") is True
    assert is_safe_url("javascript:alert(1)") is False
    assert is_safe_url("data:text/html;base64,PHNjcmlwdD4=") is False
    assert is_safe_url("file:///etc/passwd") is False
    assert is_safe_url("") is False
    assert is_safe_url(None) is False


def test_clean_query_terms():
    assert clean_query_terms("women's sage-green wrap midi dress! @#") == "women s sage-green wrap midi dress"


def test_retailer_feed_adapter_urls():
    adapter = RetailerFeedAdapter()
    query = "women sage green wrap midi dress formal office under 4000 India"

    myntra_url = adapter.build_myntra_search_url(query)
    assert "myntra.com" in myntra_url
    assert is_safe_url(myntra_url)

    ajio_url = adapter.build_ajio_search_url(query)
    assert "ajio.com/search/?text=" in ajio_url
    assert is_safe_url(ajio_url)

    nykaa_url = adapter.build_nykaa_fashion_search_url(query)
    assert "nykaafashion.com/catalogsearch/result/?q=" in nykaa_url
    assert is_safe_url(nykaa_url)

    tatacliq_url = adapter.build_tatacliq_search_url(query)
    assert "tatacliq.com/search" in tatacliq_url
    assert is_safe_url(tatacliq_url)

    amazon_url = adapter.build_amazon_in_search_url(query)
    assert "amazon.in/s?k=" in amazon_url
    assert is_safe_url(amazon_url)

    flipkart_url = adapter.build_flipkart_search_url(query)
    assert "flipkart.com/search?q=" in flipkart_url
    assert is_safe_url(flipkart_url)

    links = adapter.generate_retailer_search_links(query)
    assert len(links) >= 6
    store_names = [l.retailer for l in links]
    assert "Myntra" in store_names
    assert "AJIO" in store_names
    assert "Nykaa Fashion" in store_names
    assert "Tata CLiQ" in store_names
    assert "Amazon India" in store_names
    assert "Flipkart" in store_names


# ─────────────────────────────────────────────────────────────────────────────
# 2. Product Normalizer & Deduplication Tests
# ─────────────────────────────────────────────────────────────────────────────

def test_product_normalizer_valid_and_invalid():
    normalizer = ProductNormalizer()

    # Valid item
    raw = {
        "retailer": "Myntra",
        "title": "Sage Green Midi Dress",
        "product_url": "https://www.myntra.com/dresses/sage-123",
        "image_url": "https://images.unsplash.com/photo-123",
        "current_price_inr": 2499.0,
        "original_price_inr": 3999.0,
        "fabric_details": "100% Tencel Lyocell",
    }
    result = normalizer.normalize(raw, outfit_item_name="Sage green wrap midi dress")
    assert result is not None
    assert result.outfit_item == "Sage green wrap midi dress"
    assert result.current_price_inr == 2499.0
    assert result.original_price_inr == 3999.0
    assert result.discount_percent == 37.5
    assert result.fabric_details == "100% Tencel Lyocell"

    # Unsafe URL item should be rejected
    unsafe_raw = {
        "retailer": "ShadyStore",
        "title": "Fake Dress",
        "product_url": "javascript:alert('pwned')",
    }
    unsafe_res = normalizer.normalize(unsafe_raw)
    assert unsafe_res is None


def test_product_match_deduplication():
    match_svc = ProductMatchService()
    p1 = ProductResult(
        id="1",
        outfit_item="Midi dress",
        title="Sage Green Dress",
        retailer="Myntra",
        product_url="https://www.myntra.com/dress-1?utm_source=test",
        current_price_inr=2000,
        match_score=0.9,
        data_source="feed",
        status="verified",
        last_updated_at="2026-08-16T12:00:00Z",
    )
    p2 = ProductResult(
        id="2",
        outfit_item="Midi dress",
        title="Sage Green Dress",
        retailer="Myntra",
        product_url="https://www.myntra.com/dress-1?utm_source=different",
        current_price_inr=2000,
        match_score=0.88,
        data_source="feed",
        status="verified",
        last_updated_at="2026-08-16T12:00:00Z",
    )
    p3 = ProductResult(
        id="3",
        outfit_item="Midi dress",
        title="Linen Wrap Dress",
        retailer="AJIO",
        product_url="https://www.ajio.com/linen-wrap-dress",
        current_price_inr=2500,
        match_score=0.92,
        data_source="feed",
        status="verified",
        last_updated_at="2026-08-16T12:00:00Z",
    )

    deduped = match_svc.deduplicate([p1, p2, p3])
    assert len(deduped) == 2
    urls = [p.product_url for p in deduped]
    assert "https://www.myntra.com/dress-1?utm_source=test" in urls
    assert "https://www.ajio.com/linen-wrap-dress" in urls


# ─────────────────────────────────────────────────────────────────────────────
# 3. Price Comparison & Best Deal Calculation Tests
# ─────────────────────────────────────────────────────────────────────────────

def test_best_price_and_savings_calculation():
    comp_svc = PriceComparisonService()
    p1 = ProductResult(
        id="1",
        outfit_item="Dress",
        title="Tencel Midi Dress",
        retailer="Myntra",
        product_url="https://www.myntra.com/d1",
        current_price_inr=1999.0,
        match_score=0.95,
        sustainability_details="100% Organic Tencel",
        data_source="verified_feed",
        status="verified",
        last_updated_at="2026-08-16T12:00:00Z",
    )
    p2 = ProductResult(
        id="2",
        outfit_item="Dress",
        title="Linen Midi Dress",
        retailer="AJIO",
        product_url="https://www.ajio.com/d2",
        current_price_inr=2999.0,
        match_score=0.90,
        sustainability_details="100% Linen",
        data_source="verified_feed",
        status="verified",
        last_updated_at="2026-08-16T12:00:00Z",
    )
    p3 = ProductResult(
        id="3",
        outfit_item="Dress",
        title="Silk Anarkali",
        retailer="Tata CLiQ",
        product_url="https://www.tatacliq.com/d3",
        current_price_inr=3999.0,
        match_score=0.88,
        data_source="verified_feed",
        status="verified",
        last_updated_at="2026-08-16T12:00:00Z",
    )

    best_deal = comp_svc.find_best_deal([p1, p2, p3])
    assert best_deal is not None
    assert best_deal.best_price_product.id == "1"
    assert best_deal.best_price_product.current_price_inr == 1999.0
    assert best_deal.next_cheapest_price_inr == 2999.0
    assert best_deal.estimated_savings_inr == 1000.0
    assert best_deal.has_verified_savings is True
    assert "Verified" in best_deal.verified_source_label


# ─────────────────────────────────────────────────────────────────────────────
# 4. Price Alert & Price History Service Tests
# ─────────────────────────────────────────────────────────────────────────────

def test_price_alert_logic():
    import uuid
    from app.db.database import SessionLocal
    db = SessionLocal()
    pid = f"test_prod_{uuid.uuid4().hex[:8]}"
    try:
        alert_svc = PriceAlertService()
        req = PriceAlertCreateRequest(
            product_id=pid,
            product_title="Organic Cotton Shirt",
            product_url="https://www.myntra.com/shirt-101",
            retailer="Myntra",
            target_price_inr=1500.0,
            initial_price_inr=2000.0,
            current_price_inr=2000.0,
        )
        res = alert_svc.create_price_alert(db=db, payload=req, user_id=None)
        assert res.product_id == pid
        assert res.target_price_inr == 1500.0
        assert res.is_triggered is False

        # Simulate price drop trigger
        triggered = alert_svc.check_and_trigger_alerts(
            db=db,
            product_id=pid,
            fresh_price_inr=1450.0,
        )
        assert len(triggered) == 1
        assert triggered[0].is_triggered is True
    finally:
        db.close()


def test_price_history_snapshots():
    import uuid
    from app.db.database import SessionLocal
    db = SessionLocal()
    pid = f"test_hist_{uuid.uuid4().hex[:8]}"
    try:
        history_svc = PriceHistoryService()
        history_svc.record_snapshot(
            db=db,
            product_id=pid,
            retailer="AJIO",
            price_inr=3000.0,
            is_verified=True,
        )
        history_svc.record_snapshot(
            db=db,
            product_id=pid,
            retailer="AJIO",
            price_inr=2400.0,
            is_verified=True,
        )

        hist = history_svc.get_price_history(db=db, product_id=pid)
        assert hist.has_history is True
        assert hist.lowest_price_inr == 2400.0
        assert hist.highest_price_inr == 3000.0
        assert hist.current_price_inr == 2400.0
        assert len(hist.snapshots) == 2
    finally:
        db.close()


def test_coupon_service():
    coupon_svc = CouponService()
    all_coupons = coupon_svc.get_coupons()
    assert len(all_coupons) > 0
    myntra_coupons = coupon_svc.get_coupons(retailer="Myntra")
    assert len(myntra_coupons) > 0
    assert myntra_coupons[0].retailer == "Myntra"
    assert len(myntra_coupons[0].coupon_code) > 0


# ─────────────────────────────────────────────────────────────────────────────
# 5. FastAPI Endpoints Tests
# ─────────────────────────────────────────────────────────────────────────────

def test_api_product_search():
    payload = {
        "outfit_item_name": "Sage green wrap midi dress",
        "category": "Dress",
        "gender": "women",
        "style": "formal",
        "color": "sage green",
        "fabric": "Tencel",
        "budget_inr": 4000.0,
        "retailer_filter": "All Stores",
        "limit": 6,
    }
    response = client.post("/api/outfit-studio/products/search", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "products" in data
    assert len(data["products"]) > 0
    assert "best_deal" in data
    assert "retailer_fallback_links" in data
    assert len(data["retailer_fallback_links"]) >= 5


def test_api_product_compare_get():
    response = client.get(
        "/api/outfit-studio/products/compare",
        params={
            "outfit_item_name": "Sage green midi dress",
            "category": "Dress",
            "gender": "women",
            "budget_inr": 3500,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "products" in data
    assert len(data["products"]) > 0


def test_api_save_product():
    payload = {
        "product": {
            "id": "prod_test_save_99",
            "outfit_item": "Sage green wrap dress",
            "title": "Verified Tencel Wrap Dress",
            "retailer": "Myntra",
            "product_url": "https://www.myntra.com/dresses/tencel-wrap-dress",
            "current_price_inr": 2499.0,
            "original_price_inr": 3999.0,
            "discount_percent": 37.5,
            "match_score": 0.95,
            "data_source": "approved_affiliate_feed",
            "status": "verified",
            "last_updated_at": "2026-08-16T12:00:00Z",
        },
        "notes": "Love the sage green shade",
    }
    response = client.post("/api/outfit-studio/products/save", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["product_id"] == "prod_test_save_99"
    assert "saved" in data["message"].lower()


def test_api_price_alert():
    payload = {
        "product_id": "prod_alert_endpoint_test",
        "product_title": "Eco Linen Midi Dress",
        "product_url": "https://www.ajio.com/dresses/linen-midi",
        "retailer": "AJIO",
        "target_price_inr": 2000.0,
        "current_price_inr": 2799.0,
    }
    response = client.post("/api/outfit-studio/price-alerts", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["product_id"] == "prod_alert_endpoint_test"
    assert data["target_price_inr"] == 2000.0


def test_api_price_history_endpoint():
    response = client.get(
        "/api/outfit-studio/products/prod_history_ep/price-history",
        params={"current_price_inr": 2499.0, "retailer": "Myntra"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["product_id"] == "prod_history_ep"
    assert data["current_price_inr"] == 2499.0


def test_api_coupons_endpoint():
    response = client.get("/api/outfit-studio/coupons", params={"retailer": "AJIO"})
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert data[0]["retailer"] == "AJIO"
