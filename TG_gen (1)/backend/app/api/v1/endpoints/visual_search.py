"""
Visual Search API Endpoint
===========================
POST /api/visual-search/search
    Accepts an uploaded image + optional context, runs visual web search,
    persists results to DB, and returns structured matches with disclaimers.

POST /api/visual-search/save-match
    Saves a web match to the user's saved items.

GET  /api/visual-search/saved
    Returns all saved matches for the current user.
"""
import os
import time
import logging
from collections import defaultdict
from typing import Optional, List
from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.core.config import settings
from app.models.models import VisualSearch, VisualSearchMatch, SavedWebMatch, User
from app.schemas.schemas import (
    VisualSearchResponse, VisualSearchMatchResponse, VisualSearchQueryContext,
    SaveMatchRequest, SavedWebMatchResponse,
)
from app.services.visual_search_service import get_visual_search_service
from app.services.color_texture_processor import validate_image
from app.api.v1.dependencies import get_current_user_optional

logger = logging.getLogger(__name__)
router = APIRouter()

# ── Simple in-memory rate limiter (per IP, 10 req/min) ────────────────────────
_rate_store: dict[str, list] = defaultdict(list)
_RATE_LIMIT = 10           # max requests
_RATE_WINDOW = 60          # seconds

VISUAL_SEARCH_DISCLAIMER = (
    "These are visually similar web results. "
    "Confirm exact fabric composition through product details or garment labels. "
    "Web matches identify visually similar items only — they do NOT confirm fabric composition."
)


def _check_rate_limit(request: Request):
    """Raise 429 if the IP has exceeded the rate limit."""
    client_ip = request.client.host if request.client else "unknown"
    now = time.time()
    window_start = now - _RATE_WINDOW
    timestamps = _rate_store[client_ip]

    # Remove timestamps outside the window
    _rate_store[client_ip] = [t for t in timestamps if t > window_start]

    if len(_rate_store[client_ip]) >= _RATE_LIMIT:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded. Maximum {_RATE_LIMIT} visual searches per minute.",
        )

    _rate_store[client_ip].append(now)


@router.post("/search", response_model=VisualSearchResponse)
async def visual_search(
    request: Request,
    file: UploadFile = File(...),
    ai_predicted_fabric: Optional[str] = Form(None),
    garment_category: Optional[str] = Form(None),
    result_limit: Optional[int] = Form(None),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    """
    POST /api/visual-search/search

    Accepts a fabric/garment image and optional AI context, runs a web visual
    search via the configured provider, and returns ranked matches.

    IMPORTANT: Results are always labelled as web matches only.
    Fabric composition is never inferred from visual similarity alone.
    """
    # ── 1. Rate limiting ───────────────────────────────────────────────────────
    _check_rate_limit(request)

    # ── 2. File validation ─────────────────────────────────────────────────────
    file_bytes = await file.read()

    if not file_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    is_valid, err_msg = validate_image(file_bytes, file.filename or "upload.jpg", max_mb=settings.MAX_UPLOAD_SIZE_MB)
    if not is_valid:
        raise HTTPException(status_code=400, detail=err_msg)

    # ── 3. Determine effective result limit ────────────────────────────────────
    effective_limit = min(
        result_limit or settings.VISUAL_SEARCH_RESULT_LIMIT,
        settings.VISUAL_SEARCH_RESULT_LIMIT,
    )

    # ── 4. Run visual search ───────────────────────────────────────────────────
    svc = get_visual_search_service()

    try:
        search_result = svc.search(
            image_bytes=file_bytes,
            ai_predicted_fabric=ai_predicted_fabric,
            garment_category=garment_category,
            limit=effective_limit,
        )
    except Exception as e:
        logger.error("Visual search failed: %s", e, exc_info=True)
        # Return a graceful failure response (don't crash the endpoint)
        return VisualSearchResponse(
            search_status="failed",
            provider_used=svc.provider_name,
            query_context=VisualSearchQueryContext(
                ai_predicted_fabric=ai_predicted_fabric,
                garment_type=garment_category,
            ),
            matches=[],
            related_entities=[],
            disclaimer=VISUAL_SEARCH_DISCLAIMER,
        )

    # ── 5. Persist to database ─────────────────────────────────────────────────
    user_id = current_user.id if current_user else None
    matches = search_result["matches"]

    vs_record = VisualSearch(
        user_id=user_id,
        original_filename=file.filename,
        ai_predicted_fabric=ai_predicted_fabric,
        garment_type=garment_category,
        provider_used=search_result["provider_used"],
        search_status=search_result["search_status"],
        total_matches_returned=len(matches),
        related_entities=search_result["related_entities"],
    )
    db.add(vs_record)
    db.flush()  # get vs_record.id without committing yet

    match_responses: List[VisualSearchMatchResponse] = []
    for m in matches:
        match_row = VisualSearchMatch(
            visual_search_id=vs_record.id,
            title=m.title,
            source_url=m.source_url,
            thumbnail_url=m.thumbnail_url,
            source_domain=m.source_domain,
            match_score=m.match_score,
            detected_product_type=m.detected_product_type,
            fabric_text_found=m.fabric_text_found,
            brand=m.brand,
            price_text=m.price_text,
            source_reliability=m.source_reliability,
            verification_status=m.verification_status,
        )
        db.add(match_row)
        db.flush()

        match_responses.append(VisualSearchMatchResponse(
            id=match_row.id,
            title=m.title,
            source_url=m.source_url,
            thumbnail_url=m.thumbnail_url,
            source_domain=m.source_domain,
            match_score=m.match_score,
            detected_product_type=m.detected_product_type,
            fabric_text_found=m.fabric_text_found,
            brand=m.brand,
            price_text=m.price_text,
            source_reliability=m.source_reliability,
            verification_status=m.verification_status,
        ))

    db.commit()

    return VisualSearchResponse(
        search_id=vs_record.id,
        search_status=search_result["search_status"],
        provider_used=search_result["provider_used"],
        query_context=VisualSearchQueryContext(
            ai_predicted_fabric=ai_predicted_fabric,
            garment_type=garment_category,
        ),
        matches=match_responses,
        related_entities=search_result["related_entities"],
        disclaimer=VISUAL_SEARCH_DISCLAIMER,
    )


@router.post("/save-match", response_model=SavedWebMatchResponse, status_code=status.HTTP_201_CREATED)
def save_web_match(
    payload: SaveMatchRequest,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    """
    POST /api/visual-search/save-match
    Saves a web match as inspiration. Accepts denormalised snapshot fields
    so the saved record remains usable if the original match is later deleted.
    """
    user_id = current_user.id if current_user else None

    saved = SavedWebMatch(
        user_id=user_id,
        visual_search_match_id=payload.visual_search_match_id,
        project_id=payload.project_id,
        title=payload.title,
        source_url=payload.source_url,
        thumbnail_url=payload.thumbnail_url,
        source_domain=payload.source_domain,
        source_reliability=payload.source_reliability or "unknown",
        fabric_text_found=payload.fabric_text_found,
        match_score=payload.match_score or 0.0,
    )
    db.add(saved)
    db.commit()
    db.refresh(saved)
    return saved


@router.get("/saved", response_model=List[SavedWebMatchResponse])
def get_saved_matches(
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    """
    GET /api/visual-search/saved
    Returns all web matches saved by the current user, newest first.
    """
    user_id = current_user.id if current_user else None
    query = db.query(SavedWebMatch)
    if user_id:
        query = query.filter(SavedWebMatch.user_id == user_id)
    return query.order_by(SavedWebMatch.saved_at.desc()).all()
