from typing import List

from fastapi import APIRouter, HTTPException

from app.models.schemas import RecommendationRequest, RecommendationResponse, RestaurantOut
from app.services.dataset_service import DatasetService
from app.services.recommendation_service import RecommendationService

router = APIRouter(tags=["recommendations"])


@router.post("/recommendations", response_model=RecommendationResponse)
async def get_recommendations(payload: RecommendationRequest) -> RecommendationResponse:
    """
    Return restaurant recommendations based on user preferences.

    Phase 1:
    - Fetch data from Hugging Face dataset API (no DB/cache).
    - Filter by location, price_range, min_rating, and cuisine.
    - Rank by rating (highest first) and return top 10.
    """
    try:
        dataset_service = DatasetService()
        recommendation_service = RecommendationService(dataset_service=dataset_service)

        restaurants: List[RestaurantOut] = await recommendation_service.get_recommendations(
            preferences=payload
        )

        return RecommendationResponse(results=restaurants)
    except ValueError as exc:
        # Used for invalid/unsupported input detected in the services
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        # In a real project you would log the error.
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch restaurant data or compute recommendations.",
        ) from exc

