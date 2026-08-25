"""
AI Outfit Studio API Endpoints
================================
POST   /api/outfit/generate               – Generate a new outfit
POST   /api/outfit/{id}/regenerate-image  – Regenerate outfit image
GET    /api/outfit/history                – User's generation history (auth)
GET    /api/outfit/{id}                   – Get specific generation
POST   /api/outfit/{id}/save              – Save to profile (auth)
GET    /api/outfit/saved                  – Get saved outfits (auth)
DELETE /api/outfit/saved/{saved_id}       – Unsave outfit (auth)
"""
from __future__ import annotations

import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.api.v1.dependencies import get_db, get_current_user_optional
from app.models.models import User
from app.schemas.outfit_schemas import (
    OutfitGenerateRequest,
    OutfitGenerateResponse,
    OutfitHistoryItem,
    SaveOutfitRequest,
    SavedOutfitResponse,
)
from app.services.outfit_generator_service import get_outfit_generator_service

logger = logging.getLogger(__name__)
router = APIRouter()


def _rate_key(request: Request, user: Optional[User]) -> str:
    """Build a rate-limit key from user id or client IP."""
    if user:
        return f"user:{user.id}"
    forwarded_for = request.headers.get("X-Forwarded-For")
    ip = forwarded_for.split(",")[0].strip() if forwarded_for else request.client.host
    return f"ip:{ip}"


# ─────────────────────────────────────────────────────────────────────────────
# Generate
# ─────────────────────────────────────────────────────────────────────────────

@router.post(
    "/generate",
    response_model=OutfitGenerateResponse,
    summary="Generate an AI outfit concept with shopping links",
    tags=["AI Outfit Studio"],
)
def generate_outfit(
    payload: OutfitGenerateRequest,
    http_request: Request,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    """
    Generates a complete outfit concept from the given scenario, including:
    - Outfit name, description, and item-level breakdown
    - AI-generated outfit visualization image (labelled as AI concept)
    - Shopping product suggestions from authorized sources

    Works for both anonymous and authenticated users.
    Saving requires authentication (use POST /api/outfit/{id}/save).
    """
    service = get_outfit_generator_service()
    rate_key = _rate_key(http_request, current_user)

    try:
        result = service.generate(
            request=payload,
            db=db,
            user_id=current_user.id if current_user else None,
            rate_limit_key=rate_key,
        )
        return result
    except RuntimeError as e:
        if "rate limit" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=str(e),
            )
        logger.error("Outfit generation error: %s", e, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Outfit generation failed: {e}",
        )
    except Exception as e:
        logger.error("Unexpected error in outfit generation: %s", e, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred. Please try again.",
        )


# ─────────────────────────────────────────────────────────────────────────────
# Get specific generation
# ─────────────────────────────────────────────────────────────────────────────

@router.get(
    "/{generation_id}",
    response_model=OutfitGenerateResponse,
    summary="Get a specific outfit generation by ID",
    tags=["AI Outfit Studio"],
)
def get_outfit(
    generation_id: int,
    db: Session = Depends(get_db),
):
    service = get_outfit_generator_service()
    result = service.get_generation(generation_id, db)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Outfit generation {generation_id} not found.",
        )
    return result


# ─────────────────────────────────────────────────────────────────────────────
# Regenerate image
# ─────────────────────────────────────────────────────────────────────────────

@router.post(
    "/{generation_id}/regenerate-image",
    summary="Regenerate the outfit visualization image or specific variation",
    tags=["AI Outfit Studio"],
)
def regenerate_outfit_image(
    generation_id: int,
    variation_index: int = 1,
    db: Session = Depends(get_db),
):
    """
    Creates a new outfit visualization image for an existing generation.
    Supports regenerating a specific variation index (1 to 4).
    """
    service = get_outfit_generator_service()
    result = service.regenerate_image(generation_id, db, variation_index=variation_index)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Outfit generation {generation_id} not found.",
        )
    return result


# ─────────────────────────────────────────────────────────────────────────────
# History (auth required)
# ─────────────────────────────────────────────────────────────────────────────

@router.get(
    "/history",
    response_model=List[OutfitHistoryItem],
    summary="Get authenticated user's outfit generation history",
    tags=["AI Outfit Studio"],
)
def get_outfit_history(
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required to view history.",
        )
    service = get_outfit_generator_service()
    return service.get_history(current_user.id, db)


# ─────────────────────────────────────────────────────────────────────────────
# Save outfit (auth required)
# ─────────────────────────────────────────────────────────────────────────────

@router.post(
    "/{generation_id}/save",
    response_model=SavedOutfitResponse,
    summary="Save an outfit generation to user profile",
    tags=["AI Outfit Studio"],
)
def save_outfit(
    generation_id: int,
    payload: SaveOutfitRequest,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required to save outfits.",
        )
    service = get_outfit_generator_service()
    try:
        return service.save_outfit(
            generation_id=generation_id,
            user_id=current_user.id,
            db=db,
            project_id=payload.project_id,
            notes=payload.notes,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


# ─────────────────────────────────────────────────────────────────────────────
# Saved outfits list (auth required)
# ─────────────────────────────────────────────────────────────────────────────

@router.get(
    "/saved",
    response_model=List[OutfitHistoryItem],
    summary="Get authenticated user's saved outfits",
    tags=["AI Outfit Studio"],
)
def get_saved_outfits(
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required.",
        )
    service = get_outfit_generator_service()
    return service.get_saved_outfits(current_user.id, db)


# ─────────────────────────────────────────────────────────────────────────────
# Unsave (auth required)
# ─────────────────────────────────────────────────────────────────────────────

@router.delete(
    "/saved/{saved_id}",
    summary="Remove a saved outfit",
    tags=["AI Outfit Studio"],
)
def unsave_outfit(
    saved_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required.",
        )
    service = get_outfit_generator_service()
    deleted = service.unsave_outfit(saved_id, current_user.id, db)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Saved outfit not found.",
        )
    return {"message": "Outfit removed from saved list."}
