"""
Product Match Service
=====================
Matches and ranks products against outfit items based on category, color,
fabric, style, and keywords, and performs duplicate removal.
"""
from __future__ import annotations

import logging
import re
from typing import Any, Dict, List, Optional, Set
from urllib.parse import urlparse

from app.schemas.outfit_schemas import ProductResult

logger = logging.getLogger(__name__)


def _normalize_tokens(text: Optional[str]) -> Set[str]:
    if not text:
        return set()
    cleaned = re.sub(r"[^\w\s]", " ", text.lower())
    return {w for w in cleaned.split() if len(w) > 2}


def _detect_gender(text: Optional[str]) -> Optional[str]:
    if not text:
        return None
    lower = text.lower()
    has_men = bool(re.search(r"\b(men|mens|men's|man|male|gentleman|boy|boys)\b", lower))
    has_women = bool(re.search(r"\b(women|womens|women's|woman|female|lady|ladies|girl|girls)\b", lower))
    if has_men and not has_women:
        return "men"
    if has_women and not has_men:
        return "women"
    return None


class ProductMatchService:

    @staticmethod
    def calculate_match_score(
        product: ProductResult,
        target_category: Optional[str] = None,
        target_color: Optional[str] = None,
        target_fabric: Optional[str] = None,
        target_style: Optional[str] = None,
        target_gender: Optional[str] = None,
        target_item_name: Optional[str] = None,
        budget_inr: Optional[float] = None,
        is_budget_friendly: Optional[bool] = None,
    ) -> float:
        """
        Calculates a contextual match score between 0.0 and 0.98.
        Strictly penalizes gender mismatches to avoid cross-gender recommendations.
        """
        score = product.match_score if product.match_score > 0 else 0.75

        title_lower = product.title.lower()
        title_tokens = _normalize_tokens(product.title)
        fabric_tokens = _normalize_tokens(product.fabric_details)
        sustain_tokens = _normalize_tokens(product.sustainability_details)
        combined_tokens = title_tokens | fabric_tokens | sustain_tokens

        # Define canonical category mappings and their associated keywords
        category_aliases = {
            "jacket": {"jacket", "blazer", "bundi", "coat", "overcoat", "nehru", "suit jacket"},
            "top": {"top", "shirt", "t-shirt", "tee", "kurta", "blouse", "camisole", "tunic"},
            "bottom": {"bottom", "trousers", "trouser", "pants", "pant", "jeans", "denim", "churidar", "pyjama", "skirt", "joggers", "shorts"},
            "footwear": {"footwear", "shoe", "shoes", "brogues", "brogue", "oxford", "sneakers", "sneaker", "juttis", "jutti", "loafers", "loafer", "heels", "heel", "sandals", "sandal", "kolhapuri", "mules", "boots"},
            "dress": {"dress", "gown", "midi", "maxi", "anarkali", "saree", "robe"},
            "accessory": {"accessory", "necktie", "tie", "cufflinks", "cufflink", "belt", "watch", "hoops", "earrings", "jhumka", "dupatta", "scarf", "sunglasses"},
            "bag": {"bag", "backpack", "handbag", "tote", "duffel", "satchel", "daypack"},
        }

        def get_canonical_cat(cat_str: Optional[str], text_str: Optional[str] = "") -> Optional[str]:
            combined = f"{cat_str or ''} {text_str or ''}".lower()
            for canon, kws in category_aliases.items():
                if any(kw in combined for kw in kws):
                    return canon
            return None

        # Gender validation & discrimination
        prod_cat = getattr(product, "category", None)
        prod_gender = _detect_gender(title_lower) or _detect_gender(prod_cat)
        target_g = (target_gender or "").lower()

        # Women-specific keywords that should never appear for men
        women_specific = bool(re.search(r"\b(women|womens|women's|dress|midi|wrap dress|heels|anarkali|lehenga|saree|jhumka|skirt|gown|earrings|blouse)\b", title_lower))
        men_specific = bool(re.search(r"\b(men|mens|men's|cufflinks|oxford shoes|brogues|kurta pajam|suit for men|nehru bundi|bundi jacket)\b", title_lower))

        if target_g == "men":
            if prod_gender == "women" or (women_specific and not men_specific):
                return 0.0  # Strict rejection
        elif target_g == "women":
            if prod_gender == "men" and not women_specific:
                return 0.0  # Strict rejection

        # Strict Category Enforcement
        target_canon = get_canonical_cat(target_category, target_item_name)
        prod_canon = get_canonical_cat(prod_cat, product.title)

        if target_canon:
            if prod_canon and prod_canon != target_canon:
                # Completely incompatible category (e.g. searching for Jacket but got Accessory or Dress)
                return 0.0

        # Base relevance score starts from 0.50
        score = 0.55

        # Canonical category match bonus
        if target_canon and prod_canon and target_canon == prod_canon:
            score += 0.20

        # Gender concordance bonus
        if target_g == "men" and (prod_gender == "men" or men_specific):
            score += 0.08
        elif target_g == "women" and (prod_gender == "women" or women_specific):
            score += 0.08

        # Item name token match (e.g. "blazer", "tailored", "oxford", "silk")
        if target_item_name:
            item_tokens = _normalize_tokens(target_item_name)
            common = item_tokens & title_tokens
            if common:
                score += min(0.18, 0.06 * len(common))

        # Color match boost
        if target_color:
            color_clean = target_color.lower().strip()
            # Map hex to friendly names if needed
            hex_color_map = {
                "#1c2b4b": "navy",
                "#111213": "black",
                "#181a1b": "black",
                "#fafafa": "white",
                "#f8f1e4": "ivory",
                "#7d9b76": "sage",
                "#9b7b5b": "tan",
                "#c9a84c": "gold",
                "#5c4a3a": "earth",
                "#3a3a3a": "charcoal",
            }
            color_name = hex_color_map.get(color_clean, color_clean if not color_clean.startswith("#") else "")
            if color_name and color_name in title_lower:
                score += 0.08
            elif color_clean and not color_clean.startswith("#") and color_clean in title_lower:
                score += 0.08

        # Fabric match boost
        if target_fabric:
            fab_tokens = _normalize_tokens(target_fabric)
            if fab_tokens & combined_tokens:
                score += 0.06

        # Style match boost
        if target_style:
            style_tokens = _normalize_tokens(target_style)
            if style_tokens & combined_tokens:
                score += 0.04

        # Budget fit bonus/penalty & Budget-Friendly mode boost
        if budget_inr and product.current_price_inr:
            if product.current_price_inr <= budget_inr:
                score += 0.04
            elif product.current_price_inr > budget_inr * 1.4:
                score -= 0.05

        if is_budget_friendly and product.current_price_inr:
            # Under 1800 INR gets high budget-friendly bonus
            if product.current_price_inr <= 1800:
                score += 0.12
            elif product.current_price_inr <= 3000:
                score += 0.06
            if product.discount_percent and product.discount_percent >= 30:
                score += 0.05

        return round(max(0.0, min(0.98, score)), 2)

    @staticmethod
    def deduplicate(products: List[ProductResult]) -> List[ProductResult]:
        """
        Removes duplicate products based on normalized canonical URL
        and (retailer + normalized title).
        """
        seen_urls: Set[str] = set()
        seen_titles: Set[str] = set()
        deduped: List[ProductResult] = []

        for p in products:
            # Canonical URL key without query tracking params
            parsed_url = urlparse(p.product_url.lower())
            url_key = f"{parsed_url.netloc}{parsed_url.path}".rstrip("/")

            # Title key
            clean_title = re.sub(r"\s+", " ", re.sub(r"[^\w\s]", "", p.title.lower())).strip()
            title_key = f"{p.retailer.lower().strip()}:{clean_title}"

            if url_key in seen_urls or title_key in seen_titles:
                continue

            seen_urls.add(url_key)
            seen_titles.add(title_key)
            deduped.append(p)

        return deduped

    def match_and_rank(
        self,
        products: List[ProductResult],
        target_category: Optional[str] = None,
        target_color: Optional[str] = None,
        target_fabric: Optional[str] = None,
        target_style: Optional[str] = None,
        target_gender: Optional[str] = None,
        target_item_name: Optional[str] = None,
        budget_inr: Optional[float] = None,
        is_budget_friendly: Optional[bool] = None,
        retailer_filter: Optional[str] = None,
    ) -> List[ProductResult]:
        """
        Scores, filters, dedupes, and ranks products.
        """
        deduped = self.deduplicate(products)
        scored_products: List[ProductResult] = []

        for p in deduped:
            if retailer_filter and retailer_filter.lower() not in ("all", "all stores", "all_stores"):
                if (
                    retailer_filter.lower() not in p.retailer.lower()
                    and p.retailer.lower() not in retailer_filter.lower()
                ):
                    continue

            new_score = self.calculate_match_score(
                p,
                target_category=target_category,
                target_color=target_color,
                target_fabric=target_fabric,
                target_style=target_style,
                target_gender=target_gender,
                target_item_name=target_item_name,
                budget_inr=budget_inr,
                is_budget_friendly=is_budget_friendly,
            )
            # If severely penalized (cross-gender mismatch), skip unless no other products
            if new_score < 0.20:
                continue

            updated_p = p.model_copy(update={"match_score": new_score})
            scored_products.append(updated_p)

        # Sort by match score desc, then price asc
        scored_products.sort(
            key=lambda x: (-x.match_score, x.current_price_inr if x.current_price_inr is not None else 999999)
        )
        return scored_products


_match_service: Optional[ProductMatchService] = None

def get_product_match_service() -> ProductMatchService:
    global _match_service
    if _match_service is None:
        _match_service = ProductMatchService()
    return _match_service
