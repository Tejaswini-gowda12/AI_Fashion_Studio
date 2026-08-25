"""
Outfit Studio Mock Provider
============================
Rich deterministic mock data used when OUTFIT_LLM_PROVIDER / OUTFIT_IMAGE_PROVIDER /
OUTFIT_SHOPPING_PROVIDER are set to "mock" (the default).

Contains comprehensive, curated outfits for:
- Men's Formal & Office Attire / Suits / Shirts & Trousers
- Men's Traditional & Festive Wear
- Men's Casual Denim & Streetwear
- Women's Formal Office Ensembles & Midi Dresses
- Women's Party & Evening Looks
- Women's Traditional & Festive Anarkalis
- Unisex Sustainable Capsules
"""
from __future__ import annotations

import base64
import copy
import hashlib
import random
import re
from typing import Dict, List, Optional, Tuple

# ─────────────────────────────────────────────────────────────────────────────
# Outfit library
# ─────────────────────────────────────────────────────────────────────────────

_OUTFIT_LIBRARY: List[Dict] = [
    # ── Men – Formal / Office / Suit / Dress ───────────────────────────────────
    {
        "tags": ["formal", "office", "men", "suit", "dress", "professional", "interview", "business", "work"],
        "outfit_name": "Men's Eco-Tailored Formal Suit & Dress Set",
        "occasion": "Formal office / Business formal / Corporate",
        "description": (
            "A tailored navy sustainable suit featuring a structured organic-cotton blazer, "
            "matching slim-cut formal trousers, a crisp white bamboo-lyocell button-down shirt, "
            "vegetable-tanned leather Oxford shoes, and a recycled silk necktie."
        ),
        "items": [
            {"category": "Jacket", "name": "Navy Tailored Organic Cotton Blazer",
             "recommended_fabric": "100% GOTS Organic Cotton Twill", "color": "#1C2B4B",
             "estimated_price_inr": 3800,
             "sustainability_note": "Organic cotton twill is woven without toxic chemical sizing or synthetic pesticides."},
            {"category": "Top", "name": "Crisp White Bamboo-Lyocell Formal Shirt",
             "recommended_fabric": "100% Bamboo Lyocell", "color": "#FAFAFA",
             "estimated_price_inr": 1800,
             "sustainability_note": "Bamboo lyocell uses a non-toxic closed-loop solvent process with 90% less water."},
            {"category": "Bottom", "name": "Slim-Fit Organic Cotton Formal Trousers",
             "recommended_fabric": "100% Organic Cotton Twill", "color": "#1C2B4B",
             "estimated_price_inr": 2200,
             "sustainability_note": "Biodegradable natural fibre dyed with OEKO-TEX certified low-impact dyes."},
            {"category": "Footwear", "name": "Tan Full-Grain Oxford Brogues",
             "recommended_fabric": "Vegetable-tanned full-grain leather + cork midsole", "color": "#9B7B5B",
             "estimated_price_inr": 2800,
             "sustainability_note": "Vegetable tanning uses natural tree bark tannins; zero chrome salts."},
            {"category": "Accessory", "name": "Recycled Brass Cufflinks & Silk Tie",
             "recommended_fabric": "100% Recycled Silk & Reclaimed Brass", "color": "#C9A84C",
             "estimated_price_inr": 850,
             "sustainability_note": "Upcycled silk offcuts prevent textile waste from ending up in landfills."},
        ],
        "color_palette": ["#1C2B4B", "#FAFAFA", "#9B7B5B", "#C9A84C", "#3A3A3A"],
        "recommended_fabrics": ["Organic Cotton Twill", "Bamboo Lyocell", "Vegetable-Tanned Leather", "Recycled Silk"],
        "sustainability_summary": (
            "This men's formal suit uses 100% GOTS-certified organic cotton and closed-loop bamboo lyocell. "
            "Free of synthetic polyester linings, this ensemble is fully breathable, durable, and biodegradable."
        ),
        "sustainability_score": 91,
        "styling_tips": [
            "Pair with the tan vegetable-tanned leather Oxfords and a matching slim belt",
            "Button the top blazer button when standing; unbutton when seated for crisp drape",
            "Use minimal brass cufflinks for an understated boardroom aesthetic",
        ],
    },

    # ── Men – Traditional / Festive / Wedding ─────────────────────────────────
    {
        "tags": ["traditional", "wedding", "festive", "men", "ethnic", "kurta", "party"],
        "outfit_name": "Royal Handspun Khadi Silk Kurta & Bundi Set",
        "occasion": "Wedding guest / Festive celebration / Cultural event",
        "description": (
            "A royal ivory handspun Khadi silk kurta paired with a tailored sage-green Nehru bundi jacket, "
            "churidar trousers, and vegetable-tanned Kolhapuri juttis."
        ),
        "items": [
            {"category": "Top", "name": "Ivory Handspun Khadi Silk Kurta",
             "recommended_fabric": "Handwoven Khadi Silk", "color": "#F8F1E4",
             "estimated_price_inr": 2600,
             "sustainability_note": "Hand-spun on traditional charkhas; zero synthetic electric power looms."},
            {"category": "Jacket", "name": "Sage Green Woven Nehru Bundi Jacket",
             "recommended_fabric": "Organic Cotton-Silk Blend", "color": "#7D9B76",
             "estimated_price_inr": 2200,
             "sustainability_note": "Coloured with natural plant dyes from pomegranate rind and indigo."},
            {"category": "Bottom", "name": "Churidar Pyjama in Organic Cotton",
             "recommended_fabric": "100% Organic Cotton", "color": "#F8F1E4",
             "estimated_price_inr": 900,
             "sustainability_note": "GOTS certified cotton without chemical softeners."},
            {"category": "Footwear", "name": "Handcrafted Leather Kolhapuri Juttis",
             "recommended_fabric": "Vegetable-tanned leather", "color": "#C9A84C",
             "estimated_price_inr": 1200,
             "sustainability_note": "Artisan craft supporting rural leather artisans in Maharashtra."},
        ],
        "color_palette": ["#F8F1E4", "#7D9B76", "#C9A84C", "#2B3A6E"],
        "recommended_fabrics": ["Khadi Silk", "Organic Cotton", "Vegetable-Tanned Leather"],
        "sustainability_summary": (
            "Khadi handloom textiles consume up to 90% less energy than industrial mills "
            "and directly sustain indigenous artisan weaver clusters across India."
        ),
        "sustainability_score": 94,
        "styling_tips": [
            "Keep the Nehru collar buttoned to highlight the tailored silhouette",
            "Fold the pocket square in a simple presidential fold matching the kurta",
            "Pair with minimal brass rings or a classic chronograph watch",
        ],
    },

    # ── Men – Casual / Weekend ────────────────────────────────────────────────
    {
        "tags": ["casual", "men", "weekend", "trip", "denim", "travel"],
        "outfit_name": "Organic Denim & Hemp Weekend Kit",
        "occasion": "Weekend trip / Casual day out / Travel",
        "description": (
            "Classic relaxed-fit organic denim jeans, an indigo-wash hemp-cotton shirt, "
            "white canvas sneakers with natural rubber soles, and an organic waxed-canvas backpack."
        ),
        "items": [
            {"category": "Top", "name": "Indigo Hemp-Cotton Casual Shirt",
             "recommended_fabric": "55% Hemp / 45% Organic Cotton", "color": "#4A6FA5",
             "estimated_price_inr": 1800,
             "sustainability_note": "Hemp requires 50% less water than conventional cotton and zero pesticides."},
            {"category": "Bottom", "name": "Relaxed-Fit Organic Denim Jeans",
             "recommended_fabric": "100% Organic Cotton Denim", "color": "#3B5276",
             "estimated_price_inr": 2500,
             "sustainability_note": "Organic denim eliminates toxic synthetic chemical runoff in dyeing."},
            {"category": "Footwear", "name": "White Recycled-Canvas Low-Top Sneakers",
             "recommended_fabric": "Recycled cotton canvas + natural rubber sole", "color": "#FAFAFA",
             "estimated_price_inr": 1600,
             "sustainability_note": "Natural tapped rubber soles are biodegradable and microplastic-free."},
            {"category": "Bag", "name": "Natural Waxed Canvas Daypack",
             "recommended_fabric": "Organic beeswax-coated canvas", "color": "#C8BA9C",
             "estimated_price_inr": 1200,
             "sustainability_note": "Natural beeswax coating avoids synthetic fluoropolymer waterproofing."},
        ],
        "color_palette": ["#4A6FA5", "#3B5276", "#FAFAFA", "#C8BA9C"],
        "recommended_fabrics": ["Hemp/Organic Cotton", "Organic Denim", "Recycled Canvas", "Natural Rubber"],
        "sustainability_summary": (
            "Hemp-cotton blends use 40% less land and 50% less water than conventional cotton. "
            "Engineered for high durability and daily casual wear."
        ),
        "sustainability_score": 88,
        "styling_tips": [
            "Roll jeans twice at the hem for a clean cuff over sneakers",
            "Leave the hemp shirt unbuttoned over a plain organic cotton tee",
            "A natural cork-strap watch adds an earthy accent",
        ],
    },

    # ── Women – Party / Farewell / Evening Dress ──────────────────────────────
    {
        "tags": ["party", "farewell", "women", "celebration", "dress", "evening", "gala"],
        "outfit_name": "Sage Green Sustainable Wrap Midi Dress",
        "occasion": "College farewell / Evening party / Cocktail",
        "description": (
            "A modern sage-green wrap midi dress in flowing Tencel Lyocell fabric "
            "paired with minimal gold accessories, a vegan satin clutch, and nude block-heel sandals."
        ),
        "items": [
            {"category": "Dress", "name": "Sage Green Tencel Wrap Midi Dress",
             "recommended_fabric": "100% Tencel Lyocell", "color": "#7D9B76",
             "estimated_price_inr": 2800,
             "sustainability_note": "Tencel uses a closed-loop solvent process, recycling over 99% of solvent and water."},
            {"category": "Footwear", "name": "Nude Vegan Leather Block-Heel Sandals",
             "recommended_fabric": "PU-free vegan microfibre", "color": "#D4B896",
             "estimated_price_inr": 1400,
             "sustainability_note": "PU-free vegan leather avoids toxic polyurethane chemical baths."},
            {"category": "Bag", "name": "Mini Vegan Satin Clutch with Recycled Clasp",
             "recommended_fabric": "Recycled satin + brass clasp", "color": "#C9A84C",
             "estimated_price_inr": 750,
             "sustainability_note": "Recycled metal hardware saves virgin mining footprint."},
            {"category": "Accessory", "name": "Recycled Gold-Plated Hoop Earrings",
             "recommended_fabric": "Recycled brass, gold-plated", "color": "#C9A84C",
             "estimated_price_inr": 350,
             "sustainability_note": "Recycled metals eliminate toxic refining effluents."},
        ],
        "color_palette": ["#7D9B76", "#D4B896", "#C9A84C", "#F5F0E8"],
        "recommended_fabrics": ["Tencel/Lyocell", "Vegan microfibre", "Recycled satin"],
        "sustainability_summary": (
            "OEKO-TEX-certified Tencel saves approximately 3,500 L of water compared to conventional viscose/rayon dresses."
        ),
        "sustainability_score": 89,
        "styling_tips": [
            "Tie the wrap belt securely at the natural waist for a flattering drape",
            "Let the wrap V-neckline shine by choosing statement earrings over a necklace",
            "A light linen blazer can convert this effortlessly into a daytime look",
        ],
    },

    # ── Women – Office / Formal ────────────────────────────────────────────────
    {
        "tags": ["formal", "office", "women", "summer", "work", "suit", "professional"],
        "outfit_name": "Tailored European Linen Office Co-Ord",
        "occasion": "Formal office / Summer workwear / Board meeting",
        "description": (
            "A tailored off-white European linen blazer and wide-leg trouser suit, "
            "grounded by tan cork-soled vegan loafers and an organic canvas structured tote."
        ),
        "items": [
            {"category": "Top", "name": "Off-White Structured Linen Blazer",
             "recommended_fabric": "100% European Linen", "color": "#F5F0E8",
             "estimated_price_inr": 2400,
             "sustainability_note": "European linen is naturally rain-fed and fully biodegradable."},
            {"category": "Bottom", "name": "Wide-Leg Linen Formal Trousers",
             "recommended_fabric": "100% European Linen", "color": "#F5F0E8",
             "estimated_price_inr": 1900,
             "sustainability_note": "Flax linen cultivation requires zero synthetic nitrogen fertilizers."},
            {"category": "Footwear", "name": "Tan Cork-Sole Vegan Loafers",
             "recommended_fabric": "Cork insole + bio-PU vegan leather", "color": "#9B7B5B",
             "estimated_price_inr": 1600,
             "sustainability_note": "Cork harvesting is renewable and does not require cutting trees."},
            {"category": "Bag", "name": "Structured Canvas Laptop Tote",
             "recommended_fabric": "GOTS Certified Organic Canvas", "color": "#C8BA9C",
             "estimated_price_inr": 1100,
             "sustainability_note": "Heavyweight organic canvas is durable for years of daily office use."},
        ],
        "color_palette": ["#F5F0E8", "#9B7B5B", "#C8BA9C", "#2E2E2E"],
        "recommended_fabrics": ["European Linen", "Organic Cotton Canvas", "Cork"],
        "sustainability_summary": (
            "Linen uses 80% less water than conventional cotton and offers superior breathability in warm climates."
        ),
        "sustainability_score": 92,
        "styling_tips": [
            "Roll blazer sleeves gently for a relaxed yet sharp summer office vibe",
            "A minimalist brass collar necklace complements the tailored lapel",
            "Pair with neutral or tan footwear to elongate the wide-leg trouser silhouette",
        ],
    },

    # ── Women – Traditional / Festive / Wedding ───────────────────────────────
    {
        "tags": ["wedding", "occasion", "women", "guest", "ethnic", "traditional", "festive"],
        "outfit_name": "Ivory Handwoven Chanderi Festive Anarkali",
        "occasion": "Wedding guest / Festive celebration / Puja",
        "description": (
            "An ivory-and-gold handwoven Chanderi silk-cotton Anarkali with an indigo Ajrakh block-printed dupatta, "
            "recycled brass jhumkas, and vegetable-tanned Kolhapuri flats."
        ),
        "items": [
            {"category": "Dress", "name": "Ivory Chanderi Anarkali Kurta",
             "recommended_fabric": "Handwoven Chanderi (Silk-Cotton blend)", "color": "#F8F1E4",
             "estimated_price_inr": 3200,
             "sustainability_note": "Handwoven by traditional artisans in Madhya Pradesh on pit looms."},
            {"category": "Bottom", "name": "Palazzo Pants in Matching Chanderi",
             "recommended_fabric": "Handwoven Chanderi", "color": "#F8F1E4",
             "estimated_price_inr": 850,
             "sustainability_note": "Zero synthetic yarn; 100% natural fibre blend."},
            {"category": "Accessory", "name": "Ajrakh Indigo Block-Printed Dupatta",
             "recommended_fabric": "Organic Cotton with natural indigo mineral dye", "color": "#2B3A6E",
             "estimated_price_inr": 1100,
             "sustainability_note": "Hand block-printed with mineral dyes; zero toxic azo-dye runoff."},
            {"category": "Footwear", "name": "Gold Leather Kolhapuri Mules",
             "recommended_fabric": "Vegetable-tanned leather", "color": "#C9A84C",
             "estimated_price_inr": 800,
             "sustainability_note": "Chrome-free vegetable tanning processes."},
            {"category": "Accessory", "name": "Recycled Brass Jhumka Earrings",
             "recommended_fabric": "100% Recycled Artisan Brass", "color": "#B8860B",
             "estimated_price_inr": 400,
             "sustainability_note": "Handcrafted by metal craft artisans in Rajasthan."},
        ],
        "color_palette": ["#F8F1E4", "#C9A84C", "#2B3A6E", "#B8860B"],
        "recommended_fabrics": ["Chanderi Silk-Cotton", "Organic Cotton", "Vegetable-tanned leather"],
        "sustainability_summary": (
            "Handloom Chanderi and natural Ajrakh printing preserve Indian artisanal heritage while "
            "emitting zero industrial carbon from power looms."
        ),
        "sustainability_score": 95,
        "styling_tips": [
            "Drape the Ajrakh dupatta across one shoulder with pleats to showcase the block print border",
            "Wear the recycled brass jhumkas with hair swept in a soft bun",
            "Complement with a small silk potli bag in matching navy indigo",
        ],
    },

    # ── Unisex / Streetwear ───────────────────────────────────────────────────
    {
        "tags": ["streetwear", "unisex", "casual", "urban", "minimal"],
        "outfit_name": "Earth-Tone Recycled Street Capsule",
        "occasion": "Casual / Streetwear / Creative casual",
        "description": (
            "Oversized recycled-cotton heavyweight tee, organic fleece joggers in charcoal, "
            "chunky recycled-rubber trainers, and a deadstock upcycled canvas tote."
        ),
        "items": [
            {"category": "Top", "name": "Oversized Recycled Cotton Heavyweight Tee",
             "recommended_fabric": "100% Recycled Cotton", "color": "#5C4A3A",
             "estimated_price_inr": 1200,
             "sustainability_note": "Post-consumer recycled cotton saves 95% of water vs virgin cotton."},
            {"category": "Bottom", "name": "Organic Cotton Fleece Joggers",
             "recommended_fabric": "100% Organic Cotton Fleece", "color": "#3A3A3A",
             "estimated_price_inr": 1600,
             "sustainability_note": "GOTS certified organic fleece with zero synthetic microfibres."},
            {"category": "Footwear", "name": "Recycled Rubber Chunky Trainers",
             "recommended_fabric": "Recycled EVA offcuts + Natural Rubber", "color": "#F5F0E8",
             "estimated_price_inr": 2400,
             "sustainability_note": "Soles made from factory scrap rubber and natural hevea latex."},
            {"category": "Bag", "name": "Deadstock Canvas Upcycled Tote",
             "recommended_fabric": "Upcycled deadstock canvas", "color": "#C8BA9C",
             "estimated_price_inr": 650,
             "sustainability_note": "Reclaims fabric that was slated for landfill disposal."},
        ],
        "color_palette": ["#5C4A3A", "#3A3A3A", "#F5F0E8", "#C8BA9C"],
        "recommended_fabrics": ["Recycled Cotton", "Organic Cotton Fleece", "Recycled Rubber", "Deadstock Canvas"],
        "sustainability_summary": (
            "100% circular design using post-industrial offcuts, organic cotton, and natural rubber."
        ),
        "sustainability_score": 88,
        "styling_tips": [
            "Tuck the front of the oversized tee loosely into the joggers",
            "Wear white organic ribbed socks pulled up slightly over jogger cuffs",
            "Layer with an unbuttoned vintage flannel or denim overshirt for cool evenings",
        ],
    },
]


# ─────────────────────────────────────────────────────────────────────────────
# SVG outfit image generator
# ─────────────────────────────────────────────────────────────────────────────

def _hex_to_safe(h: str) -> str:
    """Ensure colour is a valid 6-char hex."""
    h = h.strip().lstrip("#")
    return f"#{h[:6]}" if len(h) >= 6 else "#7D9B76"


def generate_outfit_svg(
    outfit_name: str,
    items: List[Dict],
    color_palette: List[str],
    style: Optional[str] = None,
) -> str:
    """Generate a rich SVG fashion-board illustration."""
    c1 = _hex_to_safe(color_palette[0]) if len(color_palette) > 0 else "#7D9B76"
    c2 = _hex_to_safe(color_palette[1]) if len(color_palette) > 1 else "#D4B896"
    c3 = _hex_to_safe(color_palette[2]) if len(color_palette) > 2 else "#C9A84C"

    item_lines = ""
    for i, it in enumerate(items[:6]):
        y = 480 + i * 28
        cat = it.get("category", "")
        nm = it.get("name", "")[:32]
        price = it.get("estimated_price_inr", "")
        price_txt = f"₹{int(price):,}" if price else ""
        item_lines += (
            f'<text x="60" y="{y}" font-size="12" fill="#9CA3AF">'
            f'<tspan fill="{c1}" font-weight="bold">{cat}</tspan>  {nm}  '
            f'<tspan fill="{c3}">{price_txt}</tspan></text>\n'
        )

    swatches = ""
    for i, col in enumerate(color_palette[:5]):
        safe_col = _hex_to_safe(col)
        swatches += (
            f'<circle cx="{460 + i * 36}" cy="420" r="14" fill="{safe_col}" '
            f'stroke="#FFFFFF" stroke-width="1.5"/>\n'
        )

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="620" height="760"
    viewBox="0 0 620 760" style="background:#111314; font-family: \'Segoe UI\', sans-serif;">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="{c1}" stop-opacity="0.18"/>
      <stop offset="100%" stop-color="#0A0C0D" stop-opacity="0.98"/>
    </linearGradient>
    <linearGradient id="garm" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="{c2}"/>
      <stop offset="100%" stop-color="{c1}"/>
    </linearGradient>
  </defs>

  <rect width="620" height="760" fill="url(#bg)" rx="20"/>
  <rect x="0" y="0" width="620" height="64" rx="20" fill="{c1}" opacity="0.15"/>
  <rect x="24" y="14" width="220" height="30" rx="15" fill="#1C3A27" stroke="{c1}" stroke-width="1"/>
  <text x="134" y="34" font-size="11" fill="{c1}" font-weight="700" text-anchor="middle">✦ AI-GENERATED STYLE CONCEPT</text>

  <!-- Torso & Garment Silhouette -->
  <circle cx="310" cy="120" r="32" fill="{c2}" opacity="0.85"/>
  <rect x="303" y="150" width="14" height="20" fill="{c2}" opacity="0.7"/>
  <path d="M235 170 Q265 158 310 165 Q355 158 385 170 L400 315 Q310 335 220 315 Z"
        fill="url(#garm)" stroke="{c3}" stroke-width="1.5" opacity="0.92"/>
  <path d="M220 315 Q260 325 310 320 Q360 325 400 315 L415 440 L310 455 L205 440 Z"
        fill="{c1}" stroke="{c3}" stroke-width="1" opacity="0.80"/>

  <text x="60" y="410" font-size="11" fill="#6B7280" letter-spacing="2">COLOUR PALETTE</text>
  <line x1="60" y1="415" x2="560" y2="415" stroke="#374151" stroke-width="0.5"/>
  {swatches}

  <text x="60" y="468" font-size="11" fill="#6B7280" letter-spacing="2">OUTFIT BREAKDOWN</text>
  <line x1="60" y1="473" x2="560" y2="473" stroke="#374151" stroke-width="0.5"/>
  {item_lines}

  <rect x="0" y="700" width="620" height="60" fill="#0D0F10" opacity="0.9"/>
  <text x="310" y="724" font-size="15" fill="#F9F7F1" font-weight="700" text-anchor="middle">{outfit_name[:40]}</text>
  <text x="310" y="746" font-size="10" fill="#6B7280" text-anchor="middle">
    AI-generated style concept — not an exact purchasable product.</text>
</svg>'''

    b64 = base64.b64encode(svg.encode("utf-8")).decode("utf-8")
    return f"data:image/svg+xml;base64,{b64}"


# ─────────────────────────────────────────────────────────────────────────────
# Selector helpers
# ─────────────────────────────────────────────────────────────────────────────

def _score_outfit(
    outfit: Dict,
    scenario: str,
    style: Optional[str],
    gender: Optional[str],
) -> float:
    """
    Accurately scores outfits matching scenario, style, and gender.
    Prevents cross-gender mismatches (e.g. women dresses for men).
    """
    text = (scenario + " " + (style or "")).lower()
    g_pref = (gender or "").lower()
    tags = outfit.get("tags", [])

    has_men_token = bool(re.search(r"\b(men|mens|men's|man|male|gentleman|boy|boys)\b", text))
    has_women_token = bool(re.search(r"\b(women|womens|women's|woman|female|lady|ladies|girl|girls)\b", text))

    is_men = g_pref == "men" or (has_men_token and not has_women_token)
    is_women = g_pref == "women" or (has_women_token and not has_men_token)

    # Disqualify opposite gender
    if is_men and "women" in tags and "men" not in tags and "unisex" not in tags:
        return -1000.0
    if is_women and "men" in tags and "women" not in tags and "unisex" not in tags:
        return -1000.0

    score = 0.0
    if is_men and "men" in tags:
        score += 8.0
    if is_women and "women" in tags:
        score += 8.0

    # Keyword bonuses
    for tag in tags:
        if tag in text:
            score += 3.0

    if style and style.lower() in tags:
        score += 4.0

    return score


def select_outfit(
    scenario: str,
    style: Optional[str] = None,
    gender: Optional[str] = None,
    budget_inr: Optional[float] = None,
    preferred_colors: Optional[List[str]] = None,
) -> Dict:
    """Return the best-matching outfit from the library, with dynamic color/style adaptation."""
    scored = [
        (_score_outfit(o, scenario, style, gender), o)
        for o in _OUTFIT_LIBRARY
    ]
    scored.sort(key=lambda x: x[0], reverse=True)
    best = scored[0][1]

    result = copy.deepcopy(best)

    scenario_lower = (scenario or "").lower()

    # Detect color keywords in scenario
    color_map = {
        "black": "#111213",
        "charcoal": "#2E2E2E",
        "navy": "#1C2B4B",
        "blue": "#1C2B4B",
        "white": "#FAFAFA",
        "ivory": "#F8F1E4",
        "sage": "#7D9B76",
        "green": "#4E865B",
        "tan": "#9B7B5B",
        "beige": "#F5F0E8",
        "gold": "#C9A84C",
    }

    detected_color = None
    for c_name, c_hex in color_map.items():
        if re.search(rf"\b{c_name}\b", scenario_lower):
            detected_color = (c_name.capitalize(), c_hex)
            break

    if detected_color:
        c_name, c_hex = detected_color
        # Adapt top / jacket / dress item color
        for it in result.get("items", []):
            cat = it.get("category", "")
            if cat in ("Jacket", "Dress", "Top"):
                old_name = it.get("name", "")
                for old_c in ("Navy", "Ivory", "Sage Green", "Crisp White", "Off-White", "Oversized"):
                    if old_c in old_name:
                        it["name"] = old_name.replace(old_c, f"{c_name}")
                        break
                else:
                    if not any(k in old_name.lower() for k in ("black", "navy", "white", "sage", "tan")):
                        it["name"] = f"{c_name} {old_name}"
                it["color"] = c_hex

        # Prepend detected color to palette
        old_palette = result.get("color_palette", [])
        if c_hex not in old_palette:
            result["color_palette"] = [c_hex] + [c for c in old_palette if c != c_hex][:4]

        # Update outfit name if needed
        old_outfit_name = result.get("outfit_name", "")
        if "Suit" in old_outfit_name and c_name != "Navy":
            result["outfit_name"] = old_outfit_name.replace("Eco-Tailored", f"{c_name} Eco-Tailored")

    if preferred_colors:
        result["preferred_colors_hint"] = preferred_colors

    return result


def get_mock_shopping_matches(
    items: List[Dict],
    budget_inr: Optional[float] = None,
    limit: int = 8,
) -> List[Dict]:
    """Return mock shopping matches for backward compatibility."""
    return []
