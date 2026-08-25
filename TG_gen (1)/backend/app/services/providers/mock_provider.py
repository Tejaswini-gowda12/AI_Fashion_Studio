"""
Mock Visual Search Provider
============================
Returns realistic garment/fabric web matches for demo mode.
No API key required. Useful for development and testing.
"""
import random
from typing import List, Optional
from dataclasses import dataclass, field


@dataclass
class VisualMatchResult:
    """Internal data-transfer object returned by all providers."""
    title: str
    source_url: str
    thumbnail_url: Optional[str]
    source_domain: str
    match_score: float                   # 0.0 – 1.0
    detected_product_type: Optional[str] = None
    fabric_text_found: Optional[str] = None   # None = not found on source page
    brand: Optional[str] = None
    price_text: Optional[str] = None
    source_reliability: str = "unknown"       # official_brand | retailer | blog_editorial | unknown
    verification_status: str = "not_verified" # source_text_found | not_verified


# ── Static mock dataset ────────────────────────────────────────────────────────

_MOCK_MATCHES: List[dict] = [
    {
        "title": "Classic Indigo Denim Jacket — Slim Fit",
        "source_url": "https://www.levi.com/US/en_US/clothing/men/outerwear/classic-denim-jacket/p/723340001",
        "thumbnail_url": "https://images.unsplash.com/photo-1551537482-f2075a1d41f2?w=400&q=80",
        "source_domain": "levi.com",
        "match_score": 0.93,
        "detected_product_type": "Denim jacket",
        "fabric_text_found": "100% cotton denim, 12 oz. fabric weight",
        "brand": "Levi's",
        "price_text": "$89.50",
        "source_reliability": "official_brand",
        "verification_status": "source_text_found",
    },
    {
        "title": "Organic Cotton Denim Jacket — Straight Cut",
        "source_url": "https://www.patagonia.com/product/organic-denim-jacket/58240.html",
        "thumbnail_url": "https://images.unsplash.com/photo-1544966503-7cc5ac882d5d?w=400&q=80",
        "source_domain": "patagonia.com",
        "match_score": 0.89,
        "detected_product_type": "Denim jacket",
        "fabric_text_found": "100% organic cotton, Fair Trade Certified sewn",
        "brand": "Patagonia",
        "price_text": "$149.00",
        "source_reliability": "official_brand",
        "verification_status": "source_text_found",
    },
    {
        "title": "Men's Denim Trucker Jacket",
        "source_url": "https://www.gap.com/browse/product.do?pid=539128002",
        "thumbnail_url": "https://images.unsplash.com/photo-1559582798-678dfc71ccd8?w=400&q=80",
        "source_domain": "gap.com",
        "match_score": 0.85,
        "detected_product_type": "Trucker jacket",
        "fabric_text_found": "99% cotton, 1% elastane",
        "brand": "Gap",
        "price_text": "$64.95",
        "source_reliability": "retailer",
        "verification_status": "source_text_found",
    },
    {
        "title": "Denim Jacket Collection — Spring/Summer 2025",
        "source_url": "https://www.amazon.com/dp/B09XZ12345",
        "thumbnail_url": "https://images.unsplash.com/photo-1580651315530-69c8e0026377?w=400&q=80",
        "source_domain": "amazon.com",
        "match_score": 0.81,
        "detected_product_type": "Denim jacket",
        "fabric_text_found": None,
        "brand": None,
        "price_text": "$34.99",
        "source_reliability": "retailer",
        "verification_status": "not_verified",
    },
    {
        "title": "Sustainable Denim: Best Fabric Choices for Fashion Brands",
        "source_url": "https://www.fashionrevolution.org/sustainable-denim-guide-2025/",
        "thumbnail_url": "https://images.unsplash.com/photo-1528747773-9df4ff0e8de1?w=400&q=80",
        "source_domain": "fashionrevolution.org",
        "match_score": 0.72,
        "detected_product_type": None,
        "fabric_text_found": "Denim is typically 100% cotton or cotton-elastane blend; organic variants avoid pesticide-heavy cultivation.",
        "brand": None,
        "price_text": None,
        "source_reliability": "blog_editorial",
        "verification_status": "source_text_found",
    },
    {
        "title": "Washed Denim Jacket — Women's Collection",
        "source_url": "https://www2.hm.com/en_us/productpage.1234567.html",
        "thumbnail_url": "https://images.unsplash.com/photo-1594938298603-c8148c4b4571?w=400&q=80",
        "source_domain": "hm.com",
        "match_score": 0.79,
        "detected_product_type": "Denim jacket",
        "fabric_text_found": "Shell: 100% cotton. Lining: 100% polyester.",
        "brand": "H&M",
        "price_text": "$39.99",
        "source_reliability": "retailer",
        "verification_status": "source_text_found",
    },
    {
        "title": "Vintage Wash Denim Jacket",
        "source_url": "https://www.etsy.com/listing/9876543210/vintage-wash-denim-jacket",
        "thumbnail_url": "https://images.unsplash.com/photo-1571945192620-3e38fca1f73e?w=400&q=80",
        "source_domain": "etsy.com",
        "match_score": 0.74,
        "detected_product_type": "Denim jacket",
        "fabric_text_found": None,
        "brand": "IndieStitch Co.",
        "price_text": "$58.00",
        "source_reliability": "retailer",
        "verification_status": "not_verified",
    },
    {
        "title": "The Ultimate Guide to Denim Fabric Types",
        "source_url": "https://textileexchange.org/guide-denim-fabric-types/",
        "thumbnail_url": "https://images.unsplash.com/photo-1602810318383-e386cc2a3ccf?w=400&q=80",
        "source_domain": "textileexchange.org",
        "match_score": 0.68,
        "detected_product_type": None,
        "fabric_text_found": "Traditional denim: 100% cotton. Stretch denim: 98% cotton + 2% elastane. Recycled denim: 50–80% post-consumer cotton.",
        "brand": None,
        "price_text": None,
        "source_reliability": "blog_editorial",
        "verification_status": "source_text_found",
    },
    {
        "title": "Denim-Look Recycled Jacket",
        "source_url": "https://www.zara.com/us/en/recycled-denim-jacket-p02120445.html",
        "thumbnail_url": "https://images.unsplash.com/photo-1543076447-215ad9ba6923?w=400&q=80",
        "source_domain": "zara.com",
        "match_score": 0.77,
        "detected_product_type": "Jacket",
        "fabric_text_found": "65% recycled cotton, 35% recycled polyester",
        "brand": "Zara",
        "price_text": "$59.90",
        "source_reliability": "retailer",
        "verification_status": "source_text_found",
    },
    {
        "title": "Heavy Cotton Denim Jacket — Unisex",
        "source_url": "https://www.nordstrom.com/s/denim-jacket/9988776",
        "thumbnail_url": "https://images.unsplash.com/photo-1622445272461-c6580cab8755?w=400&q=80",
        "source_domain": "nordstrom.com",
        "match_score": 0.71,
        "detected_product_type": "Denim jacket",
        "fabric_text_found": None,
        "brand": "Madewell",
        "price_text": "$128.00",
        "source_reliability": "retailer",
        "verification_status": "not_verified",
    },
]

_RELATED_ENTITIES_POOL = [
    "denim jacket", "blue denim", "cotton twill", "indigo fabric",
    "washed denim", "trucker jacket", "cotton blend", "stretch denim",
    "organic cotton", "recycled denim", "selvedge denim", "rigid denim",
]


class MockVisualSearchProvider:
    """
    Demo provider that returns realistic mock matches.
    Activated when VISUAL_SEARCH_PROVIDER=mock (the default).
    """

    def search(
        self,
        image_bytes: bytes,
        ai_predicted_fabric: Optional[str] = None,
        garment_category: Optional[str] = None,
        limit: int = 10,
    ) -> tuple[List[VisualMatchResult], List[str]]:
        """
        Returns (matches, related_entities).
        Applies a small random jitter to match_score to look realistic across runs.
        """
        rng = random.Random(len(image_bytes) % 997)  # deterministic per image size

        results: List[VisualMatchResult] = []
        for raw in _MOCK_MATCHES[:limit]:
            # Small jitter ±0.03 so repeated runs feel slightly different
            jitter = rng.uniform(-0.03, 0.03)
            score = min(1.0, max(0.0, raw["match_score"] + jitter))

            results.append(VisualMatchResult(
                title=raw["title"],
                source_url=raw["source_url"],
                thumbnail_url=raw["thumbnail_url"],
                source_domain=raw["source_domain"],
                match_score=round(score, 3),
                detected_product_type=raw.get("detected_product_type"),
                fabric_text_found=raw.get("fabric_text_found"),
                brand=raw.get("brand"),
                price_text=raw.get("price_text"),
                source_reliability=raw["source_reliability"],
                verification_status=raw["verification_status"],
            ))

        # Sort by score descending
        results.sort(key=lambda r: r.match_score, reverse=True)

        # Build related entities — mix pool with AI context
        entities = list(_RELATED_ENTITIES_POOL[:6])
        if ai_predicted_fabric and ai_predicted_fabric.lower() not in [e.lower() for e in entities]:
            entities.insert(0, ai_predicted_fabric.lower())
        if garment_category and garment_category.lower() not in [e.lower() for e in entities]:
            entities.insert(1, garment_category.lower())

        return results, entities[:8]
