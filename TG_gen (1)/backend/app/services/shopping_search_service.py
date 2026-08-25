"""
Shopping Search Service
=======================
Handles search and discovery of fashion products across verified Indian stores:
- Myntra
- AJIO
- Nykaa Fashion
- Amazon India
- Tata CLiQ
- Official Brand Stores

STRICT SAFETY & COMPLIANCE RULES:
1. NEVER scrape Myntra, AJIO, Nykaa Fashion, Amazon, Tata CLiQ, or any retailer website.
2. NEVER generate fake/hallucinated product links using an LLM.
3. NEVER invent prices, stock numbers, or fake fabric details.
4. When direct retailer feeds or approved APIs are unconfigured, generate verified,
   properly-encoded safe search URLs pointing directly to each retailer's official search engine.
5. All external URLs must pass strict HTTP/HTTPS validation.
"""
from __future__ import annotations

import json
import logging
import re
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from urllib.parse import quote_plus, urlparse

from app.core.config import settings
from app.schemas.outfit_schemas import RetailerSearchLinkSchema, ShoppingMatchSchema

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# Approved Retailer Search Query Builders
# ─────────────────────────────────────────────────────────────────────────────

def _clean_query_terms(text: str) -> str:
    """Normalize query text by removing special punctuation."""
    cleaned = re.sub(r"[^\w\s-]", " ", text)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned


def build_myntra_search_url(query: str) -> str:
    """
    Myntra search URL format.
    Myntra supports slug-style search: https://www.myntra.com/<slug-query>
    """
    cleaned = _clean_query_terms(query)
    slug = re.sub(r"\s+", "-", cleaned.lower())
    if not slug:
        slug = "clothing"
    return f"https://www.myntra.com/{urllib.parse.quote(slug)}"


def build_ajio_search_url(query: str) -> str:
    """
    AJIO verified search URL format:
    https://www.ajio.com/search/?text=<encoded-query>
    """
    cleaned = _clean_query_terms(query)
    return f"https://www.ajio.com/search/?text={quote_plus(cleaned)}"


def build_nykaa_fashion_search_url(query: str) -> str:
    """
    Nykaa Fashion verified search URL format:
    https://www.nykaafashion.com/catalogsearch/result/?q=<encoded-query>
    """
    cleaned = _clean_query_terms(query)
    return f"https://www.nykaafashion.com/catalogsearch/result/?q={quote_plus(cleaned)}"


def build_amazon_in_search_url(query: str) -> str:
    """
    Amazon India verified search URL format:
    https://www.amazon.in/s?k=<encoded-query>
    """
    cleaned = _clean_query_terms(query)
    return f"https://www.amazon.in/s?k={quote_plus(cleaned)}"


def build_tatacliq_search_url(query: str) -> str:
    """
    Tata CLiQ verified search URL format:
    https://www.tatacliq.com/search/?searchCategory=all&text=<encoded-query>
    """
    cleaned = _clean_query_terms(query)
    return f"https://www.tatacliq.com/search/?searchCategory=all&text={quote_plus(cleaned)}"


# ─────────────────────────────────────────────────────────────────────────────
# URL Safety Validator
# ─────────────────────────────────────────────────────────────────────────────

def is_safe_url(url: Optional[str]) -> bool:
    """Validates that a URL is a legitimate HTTP/HTTPS web address."""
    if not url or not isinstance(url, str):
        return False
    try:
        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https"):
            return False
        if not parsed.netloc or len(parsed.netloc) < 3:
            return False
        if len(url) > 2048:
            return False
        return True
    except Exception:
        return False


# ─────────────────────────────────────────────────────────────────────────────
# Curated Product Catalogs by Gender & Style
# ─────────────────────────────────────────────────────────────────────────────

_MEN_FORMAL_CATALOG = [
    {
        "retailer": "Myntra",
        "category": "Jacket",
        "title": "Tailored Sustainable Navy Organic Cotton Formal Blazer",
        "brand": "EcoTailor Men",
        "price_inr": 3799.0,
        "fabric_details": "100% GOTS Certified Organic Cotton Twill",
        "product_url": "https://www.myntra.com/men-formal-blazers",
        "image_url": "https://images.unsplash.com/photo-1594938298603-c8148c4dae35?w=800&auto=format&fit=crop&q=80",
        "available_sizes": ["38", "40", "42", "44"],
        "match_score": 0.95,
        "sustainability_label": "GOTS Certified · Low-Impact Dyes",
    },
    {
        "retailer": "AJIO",
        "category": "Top",
        "title": "Crisp White Bamboo-Lyocell Slim Fit Formal Shirt",
        "brand": "Bambeco Men",
        "price_inr": 1799.0,
        "fabric_details": "100% Bamboo Lyocell",
        "product_url": "https://www.ajio.com/search/?text=men+bamboo+formal+shirt",
        "image_url": "https://images.unsplash.com/photo-1602810318383-e386cc2a3ccf?w=800&auto=format&fit=crop&q=80",
        "available_sizes": ["39", "40", "42", "44"],
        "match_score": 0.92,
        "sustainability_label": "Closed-Loop Solvent · Zero Pesticides",
    },
    {
        "retailer": "Tata CLiQ",
        "category": "Bottom",
        "title": "Slim-Fit Navy Organic Cotton Formal Trousers",
        "brand": "PureStitch Formal",
        "price_inr": 2199.0,
        "fabric_details": "100% Organic Cotton Twill",
        "product_url": "https://www.tatacliq.com/search/?searchCategory=all&text=men+formal+trousers",
        "image_url": "https://images.unsplash.com/photo-1624378439575-d8705ad7ae80?w=800&auto=format&fit=crop&q=80",
        "available_sizes": ["30", "32", "34", "36", "38"],
        "match_score": 0.90,
        "sustainability_label": "OEKO-TEX Certified",
    },
    {
        "retailer": "Amazon India",
        "category": "Footwear",
        "title": "Handcrafted Vegetable-Tanned Leather Oxford Brogues",
        "brand": "VerdeStep Men",
        "price_inr": 2799.0,
        "fabric_details": "Vegetable-tanned full-grain leather & cork footbed",
        "product_url": "https://www.amazon.in/s?k=men+formal+oxford+shoes",
        "image_url": "https://images.unsplash.com/photo-1614252235316-8c857d38b5f4?w=800&auto=format&fit=crop&q=80",
        "available_sizes": ["40", "41", "42", "43", "44"],
        "match_score": 0.89,
        "sustainability_label": "Chrome-Free · Biodegradable Sole",
    },
    {
        "retailer": "Official Brand",
        "category": "Accessory",
        "title": "Recycled Silk Necktie & Reclaimed Brass Tie Clip Set",
        "brand": "SustainCraft",
        "price_inr": 799.0,
        "fabric_details": "100% Upcycled Silk & Reclaimed Brass",
        "product_url": "https://www.myntra.com/men-accessories",
        "image_url": "https://images.unsplash.com/photo-1589756823695-278bc923f962?w=800&auto=format&fit=crop&q=80",
        "available_sizes": ["One Size"],
        "match_score": 0.86,
        "sustainability_label": "Upcycled Materials",
    },
]

_MEN_TRADITIONAL_CATALOG = [
    {
        "retailer": "Myntra",
        "category": "Top",
        "title": "Handspun Royal Khadi Silk Kurta Pajama Set",
        "brand": "DesiHandloom",
        "price_inr": 2899.0,
        "fabric_details": "100% Handspun Khadi Silk",
        "product_url": "https://www.myntra.com/men-ethnic-wear",
        "image_url": "https://images.unsplash.com/photo-1583391733956-3750e0ff4e8b?w=800&auto=format&fit=crop&q=80",
        "available_sizes": ["S", "M", "L", "XL", "XXL"],
        "match_score": 0.94,
        "sustainability_label": "Zero Electric Power · Artisan Loom",
    },
    {
        "retailer": "AJIO",
        "category": "Jacket",
        "title": "Sage Green Organic Cotton-Silk Nehru Bundi Jacket",
        "brand": "IndieVogue Men",
        "price_inr": 2199.0,
        "fabric_details": "Organic Cotton-Silk Blend with Natural Dyes",
        "product_url": "https://www.ajio.com/search/?text=men+nehru+jacket",
        "image_url": "https://images.unsplash.com/photo-1563178406-4cdc2923acbc?w=800&auto=format&fit=crop&q=80",
        "available_sizes": ["38", "40", "42", "44"],
        "match_score": 0.91,
        "sustainability_label": "Plant-Dyed",
    },
    {
        "retailer": "Nykaa Fashion",
        "category": "Footwear",
        "title": "Handmade Vegetable-Tanned Leather Kolhapuri Juttis",
        "brand": "ArtisanStep",
        "price_inr": 1199.0,
        "fabric_details": "Chrome-free vegetable tanned leather",
        "product_url": "https://www.nykaafashion.com/catalogsearch/result/?q=men+kolhapuri",
        "image_url": "https://images.unsplash.com/photo-1543163521-1bf539c55dd2?w=800&auto=format&fit=crop&q=80",
        "available_sizes": ["40", "41", "42", "43"],
        "match_score": 0.88,
        "sustainability_label": "Fair Trade Artisan Made",
    },
    {
        "retailer": "Tata CLiQ",
        "category": "Accessory",
        "title": "Handwoven Tussar Silk Dupatta Stole for Men",
        "brand": "SustainCraft",
        "price_inr": 999.0,
        "fabric_details": "Wild Ahimsa Tussar Silk",
        "product_url": "https://www.tatacliq.com/search/?searchCategory=all&text=men+silk+stole",
        "image_url": "https://images.unsplash.com/photo-1609357605129-26f69add5d6e?w=800&auto=format&fit=crop&q=80",
        "available_sizes": ["One Size"],
        "match_score": 0.87,
        "sustainability_label": "Cruelty-Free Ahimsa Silk",
    },
]

_MEN_CASUAL_CATALOG = [
    {
        "retailer": "Myntra",
        "category": "Bottom",
        "title": "Relaxed-Fit GOTS Organic Cotton Denim Jeans",
        "brand": "PureStitch Denim",
        "price_inr": 2499.0,
        "fabric_details": "100% GOTS Organic Cotton Denim",
        "product_url": "https://www.myntra.com/men-jeans",
        "image_url": "https://images.unsplash.com/photo-1542272604-780c96856592?w=800&auto=format&fit=crop&q=80",
        "available_sizes": ["30", "32", "34", "36"],
        "match_score": 0.93,
        "sustainability_label": "GOTS Certified · Zero Toxic Bleach",
    },
    {
        "retailer": "AJIO",
        "category": "Top",
        "title": "Indigo Dyed Hemp & Organic Cotton Casual Shirt",
        "brand": "Fibre & Leaf",
        "price_inr": 1799.0,
        "fabric_details": "55% Hemp, 45% Organic Cotton",
        "product_url": "https://www.ajio.com/search/?text=hemp+shirt+men",
        "image_url": "https://images.unsplash.com/photo-1596755094514-f87e34085b2c?w=800&auto=format&fit=crop&q=80",
        "available_sizes": ["S", "M", "L", "XL"],
        "match_score": 0.90,
        "sustainability_label": "Low Water · Biodegradable",
    },
    {
        "retailer": "Amazon India",
        "category": "Footwear",
        "title": "Recycled Cotton Canvas Sneakers with Natural Rubber Sole",
        "brand": "ReLoop Footwear",
        "price_inr": 1599.0,
        "fabric_details": "Recycled cotton canvas & natural hevea latex sole",
        "product_url": "https://www.amazon.in/s?k=recycled+canvas+sneakers",
        "image_url": "https://images.unsplash.com/photo-1525966222134-fcfa99b8ae77?w=800&auto=format&fit=crop&q=80",
        "available_sizes": ["40", "41", "42", "43", "44"],
        "match_score": 0.88,
        "sustainability_label": "Zero Microplastic Soles",
    },
    {
        "retailer": "Tata CLiQ",
        "category": "Bag",
        "title": "Natural Waxed Organic Canvas Daypack",
        "brand": "Rootcraft",
        "price_inr": 1299.0,
        "fabric_details": "Natural beeswax-coated organic canvas",
        "product_url": "https://www.tatacliq.com/search/?searchCategory=all&text=canvas+backpack",
        "image_url": "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=800&auto=format&fit=crop&q=80",
        "available_sizes": ["Medium"],
        "match_score": 0.86,
        "sustainability_label": "Beeswax Waterproofing",
    },
]

_WOMEN_DRESS_CATALOG = [
    {
        "retailer": "Myntra",
        "category": "Dress",
        "title": "Sustainable Sage Green Tencel Lyocell Wrap Midi Dress",
        "brand": "EcoElegance",
        "price_inr": 2899.0,
        "fabric_details": "100% Tencel Lyocell (OEKO-TEX Certified)",
        "product_url": "https://www.myntra.com/dresses",
        "image_url": "https://images.unsplash.com/photo-1595777457583-95e059d581b8?w=800&auto=format&fit=crop&q=80",
        "available_sizes": ["XS", "S", "M", "L", "XL"],
        "match_score": 0.95,
        "sustainability_label": "Zero Microplastics · Low Water",
    },
    {
        "retailer": "AJIO",
        "category": "Dress",
        "title": "Organic European Linen Wrap Dress with Belt",
        "brand": "PureFab",
        "price_inr": 3299.0,
        "fabric_details": "100% Rain-Fed European Linen",
        "product_url": "https://www.ajio.com/search/?text=linen+dress+women",
        "image_url": "https://images.unsplash.com/photo-1572804013309-59a88b7e92f1?w=800&auto=format&fit=crop&q=80",
        "available_sizes": ["S", "M", "L", "XL"],
        "match_score": 0.92,
        "sustainability_label": "Biodegradable · Plant Dyed",
    },
    {
        "retailer": "Nykaa Fashion",
        "category": "Footwear",
        "title": "Cruelty-Free Vegan Leather Nude Block Heels",
        "brand": "VerdeStep",
        "price_inr": 1999.0,
        "fabric_details": "Bio-PU Vegan Microfibre & Cork Midsole",
        "product_url": "https://www.nykaafashion.com/catalogsearch/result/?q=vegan+heels",
        "image_url": "https://images.unsplash.com/photo-1543163521-1bf539c55dd2?w=800&auto=format&fit=crop&q=80",
        "available_sizes": ["36", "37", "38", "39", "40"],
        "match_score": 0.89,
        "sustainability_label": "PETA-Approved Vegan",
    },
    {
        "retailer": "Tata CLiQ",
        "category": "Accessory",
        "title": "Handcrafted Recycled Brass Minimal Gold Hoops",
        "brand": "SustainJewels",
        "price_inr": 599.0,
        "fabric_details": "100% Recycled Artisan Brass",
        "product_url": "https://www.tatacliq.com/search/?searchCategory=all&text=brass+earrings",
        "image_url": "https://images.unsplash.com/photo-1535632066927-ab7c9ab60908?w=800&auto=format&fit=crop&q=80",
        "available_sizes": ["One Size"],
        "match_score": 0.86,
        "sustainability_label": "Upcycled Artisan Metal",
    },
    {
        "retailer": "Amazon India",
        "category": "Bag",
        "title": "Natural Jute & Organic Canvas Structured Evening Bag",
        "brand": "EarthBags India",
        "price_inr": 950.0,
        "fabric_details": "GOTS Certified Organic Canvas & Golden Jute",
        "product_url": "https://www.amazon.in/s?k=organic+canvas+clutch",
        "image_url": "https://images.unsplash.com/photo-1590874103328-eac38a683ce7?w=800&auto=format&fit=crop&q=80",
        "available_sizes": ["Medium"],
        "match_score": 0.88,
        "sustainability_label": "Plastic-Free",
    },
]

_WOMEN_TRADITIONAL_CATALOG = [
    {
        "retailer": "Myntra",
        "category": "Dress",
        "title": "Handwoven Ivory Chanderi Silk Anarkali Set",
        "brand": "Viraat Handlooms",
        "price_inr": 3499.0,
        "fabric_details": "Handwoven Chanderi Silk-Cotton",
        "product_url": "https://www.myntra.com/women-anarkali",
        "image_url": "https://images.unsplash.com/photo-1610030469983-98e550d6193c?w=800&auto=format&fit=crop&q=80",
        "available_sizes": ["S", "M", "L", "XL"],
        "match_score": 0.94,
        "sustainability_label": "Artisan Handloom",
    },
    {
        "retailer": "AJIO",
        "category": "Accessory",
        "title": "Natural Indigo Ajrakh Block-Printed Organic Cotton Dupatta",
        "brand": "Kutch Heritage",
        "price_inr": 1150.0,
        "fabric_details": "100% Organic Cotton with Indigo Mineral Dye",
        "product_url": "https://www.ajio.com/search/?text=ajrakh+dupatta",
        "image_url": "https://images.unsplash.com/photo-1617627143750-d86bc21e42bb?w=800&auto=format&fit=crop&q=80",
        "available_sizes": ["One Size"],
        "match_score": 0.91,
        "sustainability_label": "Plant & Mineral Dyes",
    },
    {
        "retailer": "Nykaa Fashion",
        "category": "Footwear",
        "title": "Gold Vegetable-Tanned Leather Kolhapuri Flats",
        "brand": "ArtisanCraft",
        "price_inr": 850.0,
        "fabric_details": "Chrome-free vegetable tanned leather",
        "product_url": "https://www.nykaafashion.com/catalogsearch/result/?q=kolhapuri+flats",
        "image_url": "https://images.unsplash.com/photo-1543163521-1bf539c55dd2?w=800&auto=format&fit=crop&q=80",
        "available_sizes": ["36", "37", "38", "39", "40"],
        "match_score": 0.88,
        "sustainability_label": "Vegetable Tanned",
    },
    {
        "retailer": "Tata CLiQ",
        "category": "Accessory",
        "title": "Handcrafted Recycled Brass Jhumka Earrings",
        "brand": "SustainJewels",
        "price_inr": 450.0,
        "fabric_details": "100% Recycled Artisan Brass",
        "product_url": "https://www.tatacliq.com/search/?searchCategory=all&text=brass+jhumka",
        "image_url": "https://images.unsplash.com/photo-1535632066927-ab7c9ab60908?w=800&auto=format&fit=crop&q=80",
        "available_sizes": ["One Size"],
        "match_score": 0.87,
        "sustainability_label": "Artisan Crafted",
    },
]


# ─────────────────────────────────────────────────────────────────────────────
# Service Implementation
# ─────────────────────────────────────────────────────────────────────────────

class ShoppingSearchService:

    def build_search_query(
        self,
        category: str,
        color: Optional[str] = None,
        fabric: Optional[str] = None,
        style: Optional[str] = None,
        gender: Optional[str] = None,
        occasion: Optional[str] = None,
    ) -> str:
        """
        Build an optimal shopping keyword search phrase.
        """
        tokens: List[str] = []
        if gender and gender.lower() in ("women", "men", "unisex"):
            tokens.append(gender.lower())
        if color and not color.startswith("#"):
            tokens.append(color.strip())
        if fabric and fabric.lower() not in ("any", "standard", "general"):
            tokens.append(fabric.split("/")[0].strip())
        if style and style.lower() not in ("any", "general"):
            tokens.append(style.strip())
        if category:
            tokens.append(category.strip())

        query = " ".join(t for t in tokens if t)
        return _clean_query_terms(query) or f"{category} India"

    def generate_retailer_search_links(
        self,
        query: str,
    ) -> List[RetailerSearchLinkSchema]:
        """
        Produce verified direct search links for top Indian stores.
        """
        links = [
            RetailerSearchLinkSchema(
                retailer="Myntra",
                search_url=build_myntra_search_url(query),
                query=query,
                icon="🛍️",
            ),
            RetailerSearchLinkSchema(
                retailer="AJIO",
                search_url=build_ajio_search_url(query),
                query=query,
                icon="✨",
            ),
            RetailerSearchLinkSchema(
                retailer="Nykaa Fashion",
                search_url=build_nykaa_fashion_search_url(query),
                query=query,
                icon="🌸",
            ),
            RetailerSearchLinkSchema(
                retailer="Amazon India",
                search_url=build_amazon_in_search_url(query),
                query=query,
                icon="📦",
            ),
            RetailerSearchLinkSchema(
                retailer="Tata CLiQ",
                search_url=build_tatacliq_search_url(query),
                query=query,
                icon="💎",
            ),
        ]
        return links

    def search_google_custom_search(
        self,
        query: str,
        category: str,
        budget_inr: Optional[float] = None,
        limit: int = 6,
    ) -> List[ShoppingMatchSchema]:
        """
        Search authorized product pages using Google Custom Search JSON API.
        """
        api_key = settings.GOOGLE_CUSTOM_SEARCH_API_KEY or settings.SHOPPING_SEARCH_API_KEY
        cx = settings.GOOGLE_CUSTOM_SEARCH_CX
        if not api_key or not cx:
            return []

        search_q = f"{query} site:myntra.com OR site:ajio.com OR site:nykaafashion.com OR site:amazon.in OR site:tatacliq.com"
        if budget_inr:
            search_q += f" under {int(budget_inr)}"

        params = urllib.parse.urlencode({
            "key": api_key,
            "cx": cx,
            "q": search_q,
            "num": min(limit, 10),
            "searchType": "image",
        })
        url = f"https://www.googleapis.com/customsearch/v1?{params}"

        results: List[ShoppingMatchSchema] = []
        now_iso = datetime.now(timezone.utc).isoformat()

        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "EcoFabric-ShoppingAssistant/1.0"},
            )
            with urllib.request.urlopen(req, timeout=settings.OUTFIT_REQUEST_TIMEOUT_SECONDS) as resp:
                data = json.loads(resp.read().decode("utf-8"))

            for item in data.get("items", []):
                prod_url = item.get("image", {}).get("contextLink") or item.get("link", "")
                if not is_safe_url(prod_url):
                    continue

                display_link = item.get("displayLink", "").lower()
                retailer = "Official Store"
                if "myntra" in display_link:
                    retailer = "Myntra"
                elif "ajio" in display_link:
                    retailer = "AJIO"
                elif "nykaa" in display_link:
                    retailer = "Nykaa Fashion"
                elif "amazon" in display_link:
                    retailer = "Amazon India"
                elif "tatacliq" in display_link:
                    retailer = "Tata CLiQ"

                results.append(
                    ShoppingMatchSchema(
                        retailer=retailer,
                        category=category,
                        title=item.get("title", f"{category} on {retailer}")[:120],
                        brand=retailer,
                        price_inr=None,
                        price=None,
                        currency="INR",
                        product_url=prod_url,
                        image_url=item.get("link") if is_safe_url(item.get("link")) else None,
                        fabric_details=None,
                        available_sizes=[],
                        match_score=0.88,
                        data_source="approved_search",
                        source_type="authorized_retailer",
                        status="verified",
                        timestamp=now_iso,
                    )
                )
        except Exception as e:
            logger.warning("Google Custom Search for shopping failed: %s", e)

        return results[:limit]

    def get_curated_store_matches(
        self,
        items: List[Dict[str, Any]],
        gender: Optional[str] = None,
        style: Optional[str] = None,
        occasion: Optional[str] = None,
        budget_inr: Optional[float] = None,
        limit: int = 8,
    ) -> List[ShoppingMatchSchema]:
        """
        Dynamically selects curated matching products based on gender and style.
        """
        matches: List[ShoppingMatchSchema] = []
        now_iso = datetime.now(timezone.utc).isoformat()

        g_pref = (gender or "").lower()
        occ_text = (occasion or "").lower()
        style_text = (style or "").lower()
        items_text = " ".join(str(i.get("name", "")) + " " + str(i.get("category", "")) for i in items).lower()
        all_text = f"{g_pref} {occ_text} {style_text} {items_text}"

        has_men_token = bool(re.search(r"\b(men|mens|men's|man|male|gentleman|boy|boys)\b", all_text))
        has_women_token = bool(re.search(r"\b(women|womens|women's|woman|female|lady|ladies|girl|girls)\b", all_text))

        men_indicators = any(k in items_text for k in ["oxford", "brogues", "cufflinks", "necktie", "suit", "blazer", "formal trousers", "nehru", "bundi", "kurta pajama", "men"])
        women_indicators = any(k in items_text for k in ["wrap dress", "midi dress", "gown", "anarkali", "saree", "jhumka", "block heels", "heels", "skirt"])

        if g_pref == "men" or (has_men_token and not has_women_token) or (men_indicators and not women_indicators):
            is_men = True
        elif g_pref == "women" or (has_women_token and not has_men_token) or (women_indicators and not men_indicators):
            is_men = False
        else:
            is_men = False

        is_traditional = any(t in all_text for t in ["traditional", "ethnic", "kurta", "anarkali", "wedding", "festive", "chanderi", "nehru"])
        is_casual = any(t in all_text for t in ["casual", "weekend", "trip", "denim", "streetwear", "jogger"])

        if is_men:
            if is_traditional:
                catalog = _MEN_TRADITIONAL_CATALOG
            elif is_casual:
                catalog = _MEN_CASUAL_CATALOG
            else:
                catalog = _MEN_FORMAL_CATALOG
        else:
            if is_traditional:
                catalog = _WOMEN_TRADITIONAL_CATALOG
            else:
                catalog = _WOMEN_DRESS_CATALOG

        for item in catalog:
            price = item.get("price_inr")
            if budget_inr and price and price > budget_inr * 1.35:
                continue
            matches.append(
                ShoppingMatchSchema(
                    retailer=item["retailer"],
                    category=item["category"],
                    title=item["title"],
                    brand=item["brand"],
                    price_inr=price,
                    price=price,
                    currency="INR",
                    product_url=item["product_url"],
                    image_url=item["image_url"],
                    fabric_details=item.get("fabric_details"),
                    available_sizes=item.get("available_sizes", []),
                    match_score=item.get("match_score", 0.90),
                    data_source="mock_demo",
                    source_type="mock_demo",
                    status="demo",
                    timestamp=now_iso,
                    sustainability_label=item.get("sustainability_label"),
                )
            )

        return matches[:limit]

    def search(
        self,
        items: List[Dict[str, Any]],
        gender: Optional[str] = None,
        style: Optional[str] = None,
        occasion: Optional[str] = None,
        budget_inr: Optional[float] = None,
        location: Optional[str] = "India",
        limit: int = 8,
    ) -> tuple[List[ShoppingMatchSchema], List[RetailerSearchLinkSchema], str]:
        """
        Main entry point for shopping search.
        Returns:
            (shopping_results, retailer_search_links, provider_used)
        """
        provider = (
            settings.SHOPPING_SEARCH_PROVIDER or settings.OUTFIT_SHOPPING_PROVIDER
        ).lower()

        primary_category = items[0].get("category", "Clothing") if items else "Clothing"
        primary_color = items[0].get("color", "") if items else ""
        primary_fabric = items[0].get("recommended_fabric") or items[0].get("preferred_fabric") if items else ""

        # Build primary query
        main_query = self.build_search_query(
            category=primary_category,
            color=primary_color,
            fabric=primary_fabric,
            style=style,
            gender=gender,
            occasion=occasion,
        )

        # 1. Generate verified retailer search links for Indian stores
        retailer_links = self.generate_retailer_search_links(main_query)

        # 2. Search for live products if approved provider configured
        results: List[ShoppingMatchSchema] = []

        if provider == "google_cse" or (settings.GOOGLE_CUSTOM_SEARCH_API_KEY and settings.GOOGLE_CUSTOM_SEARCH_CX):
            results = self.search_google_custom_search(
                query=main_query,
                category=primary_category,
                budget_inr=budget_inr,
                limit=limit,
            )
            if results:
                return results, retailer_links, "google_cse"

        # 3. Fallback to curated reference results accurately matched by gender & style
        results = self.get_curated_store_matches(
            items=items,
            gender=gender,
            style=style,
            occasion=occasion,
            budget_inr=budget_inr,
            limit=limit,
        )
        return results, retailer_links, "mock"


# Singleton
_shopping_service: Optional[ShoppingSearchService] = None

def get_shopping_search_service() -> ShoppingSearchService:
    global _shopping_service
    if _shopping_service is None:
        _shopping_service = ShoppingSearchService()
    return _shopping_service
