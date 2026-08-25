import io
import pytest
from PIL import Image
from fastapi.testclient import TestClient

from app.main import app
from app.services.providers.mock_provider import MockVisualSearchProvider, VisualMatchResult
from app.services.providers.google_vision_provider import (
    classify_domain,
    extract_fabric_text,
    _safe_domain,
)
from app.services.visual_search_service import (
    VisualSearchService,
    _deduplicate,
    _is_safe_url,
    get_visual_search_service,
)

client = TestClient(app)


def _generate_test_image_bytes(width=600, height=600, color="navy") -> bytes:
    img = Image.new("RGB", (width, height), color=color)
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


# ── 1. Provider Fallback and Selection ──────────────────────────────────────────

def test_mock_provider_fallback():
    """Verify that Mock provider works and returns realistic formatted matches."""
    provider = MockVisualSearchProvider()
    img_bytes = _generate_test_image_bytes()
    matches, entities = provider.search(
        img_bytes,
        ai_predicted_fabric="Denim",
        garment_category="Jacket",
        limit=5,
    )

    assert len(matches) <= 5
    assert len(matches) > 0
    assert any("denim" in e.lower() or "jacket" in e.lower() for e in entities)

    for m in matches:
        assert isinstance(m, VisualMatchResult)
        assert m.match_score >= 0.0 and m.match_score <= 1.0
        assert m.source_url.startswith("http")
        assert m.source_reliability in ["official_brand", "retailer", "blog_editorial", "unknown"]
        assert m.verification_status in ["source_text_found", "not_verified"]


def test_visual_search_service_factory():
    """Verify factory returns a valid VisualSearchService instance."""
    svc = get_visual_search_service()
    assert isinstance(svc, VisualSearchService)
    assert svc.provider_name in ["mock", "google_vision", "bing"]


# ── 2. Deduplication and URL Safety ───────────────────────────────────────────

def test_duplicate_result_removal():
    """Verify that matches with duplicate source URLs are deduplicated, keeping highest score."""
    match1 = VisualMatchResult(
        title="Jacket 1",
        source_url="https://example.com/product/1",
        thumbnail_url=None,
        source_domain="example.com",
        match_score=0.75,
        source_reliability="retailer",
    )
    match2 = VisualMatchResult(
        title="Jacket 1 Duplicate",
        source_url="https://example.com/product/1",
        thumbnail_url=None,
        source_domain="example.com",
        match_score=0.92,
        source_reliability="retailer",
    )
    match3 = VisualMatchResult(
        title="Jacket 2",
        source_url="https://example.com/product/2",
        thumbnail_url=None,
        source_domain="example.com",
        match_score=0.80,
        source_reliability="retailer",
    )

    deduped = _deduplicate([match1, match2, match3])
    assert len(deduped) == 2
    # The duplicate url should keep the higher score (0.92)
    url1_match = next(m for m in deduped if m.source_url == "https://example.com/product/1")
    assert url1_match.match_score == 0.92


def test_safe_url_handling():
    """Verify unsafe, malformed, or malicious URL schemes are filtered out."""
    assert _is_safe_url("https://www.levi.com/product") is True
    assert _is_safe_url("http://example.com/item") is True
    assert _is_safe_url("javascript:alert(1)") is False
    assert _is_safe_url("data:image/png;base64,abc") is False
    assert _is_safe_url("ftp://server.com/file") is False
    assert _is_safe_url("") is False


# ── 3. Source Reliability Classification ──────────────────────────────────────

def test_source_reliability_classification():
    """Test domain categorization for brand, retailer, blog, and unknown."""
    assert classify_domain("levi.com") == "official_brand"
    assert classify_domain("www.patagonia.com") == "official_brand"
    assert classify_domain("nike.com") == "official_brand"

    assert classify_domain("amazon.com") == "retailer"
    assert classify_domain("www.nordstrom.com") == "retailer"
    assert classify_domain("zara.com") == "retailer"
    assert classify_domain("etsy.com") == "retailer"

    assert classify_domain("fashionrevolution.org") == "blog_editorial"
    assert classify_domain("textile-guide-blog.com") == "blog_editorial"

    assert classify_domain("randomunregisteredwebsite992.com") == "unknown"


# ── 4. Fabric Composition Extraction vs Non-Confirmed Labels ──────────────────

def test_fabric_text_extraction_and_labeling():
    """Verify that composition is only extracted if explicitly stated, never inferred."""
    text_with_fabric = "Crafted from 100% organic cotton denim with copper rivets."
    assert extract_fabric_text(text_with_fabric) is not None
    assert "100% organic cotton" in extract_fabric_text(text_with_fabric).lower()

    text_with_blend = "Features 65% recycled cotton, 35% polyester blend."
    assert extract_fabric_text(text_with_blend) is not None

    text_generic = "Classic blue casual style jacket for all seasons."
    assert extract_fabric_text(text_generic) is None


# ── 5. Endpoints: Search, Save Match, Get Saved ───────────────────────────────

def test_visual_search_endpoint():
    """Test POST /api/visual-search/search returns compliant response format."""
    img_bytes = _generate_test_image_bytes(512, 512)
    files = {"file": ("fabric.jpg", img_bytes, "image/jpeg")}
    data = {
        "ai_predicted_fabric": "Denim",
        "garment_category": "Jacket",
        "result_limit": "6",
    }

    res = client.post("/api/visual-search/search", files=files, data=data)
    assert res.status_code == 200
    json_data = res.json()

    assert json_data["search_status"] in ["success", "no_results"]
    assert "query_context" in json_data
    assert json_data["query_context"]["ai_predicted_fabric"] == "Denim"
    assert json_data["query_context"]["garment_type"] == "Jacket"
    assert "matches" in json_data
    assert "disclaimer" in json_data
    assert "visually similar" in json_data["disclaimer"].lower()

    # Verify match structure
    for match in json_data["matches"]:
        assert "title" in match
        assert "source_url" in match
        assert "source_reliability" in match
        assert "verification_status" in match
        assert match["match_score"] >= 0.0


def test_save_and_retrieve_web_match():
    """Test saving a visual web match and retrieving saved matches."""
    save_payload = {
        "title": "Levi's Denim Jacket",
        "source_url": "https://www.levi.com/test-jacket",
        "thumbnail_url": "https://images.unsplash.com/photo-1551537482-f2075a1d41f2",
        "source_domain": "levi.com",
        "source_reliability": "official_brand",
        "fabric_text_found": "100% cotton denim",
        "match_score": 0.94,
    }

    save_res = client.post("/api/visual-search/save-match", json=save_payload)
    assert save_res.status_code == 201
    saved_item = save_res.json()
    assert saved_item["source_url"] == "https://www.levi.com/test-jacket"
    assert saved_item["source_reliability"] == "official_brand"
    assert saved_item["fabric_text_found"] == "100% cotton denim"

    # Fetch saved items
    get_res = client.get("/api/visual-search/saved")
    assert get_res.status_code == 200
    saved_list = get_res.json()
    assert isinstance(saved_list, list)
    assert any(s["source_url"] == "https://www.levi.com/test-jacket" for s in saved_list)
