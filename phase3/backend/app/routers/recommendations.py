from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.schemas import (
    RecommendationRequest,
    RecommendationResponse,
    RestaurantOut,
)
from app.services.dataset_service import DatasetService
from app.services.recommendation_service import RecommendationService

router = APIRouter(tags=["recommendations"])


@router.post("/recommendations", response_model=RecommendationResponse)
async def get_recommendations(
    payload: RecommendationRequest,
    db: Session = Depends(get_db),
) -> RecommendationResponse:
    """
    Return restaurant recommendations based on user preferences.

    Phase 3:
    - Use a local database of restaurants populated from the Hugging Face dataset on first use.
    - Filter by location, price_range, min_rating, and cuisine.
    - Rank by rating (highest first) and return top 10.
    - Optionally call Groq LLM (if GROQ_API_KEY is set) to generate an overall summary.
    """
    try:
        dataset_service = DatasetService()
        recommendation_service = await RecommendationService.create(
            dataset_service=dataset_service,
            db=db,
        )

        restaurants: List[RestaurantOut]
        response = await recommendation_service.get_recommendations(preferences=payload)

        return response
    except ValueError as exc:
        # Used for invalid/unsupported input detected in the services
        raise HTTPException(status_code=400, detail=str(exc)) from exc

