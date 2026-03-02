from typing import List

from fastapi import APIRouter, Depends, HTTPException

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
    db = Depends(get_db),
) -> RecommendationResponse:
    try:
        dataset_service = DatasetService()
        recommendation_service = await RecommendationService.create(
            dataset_service=dataset_service,
            db=db,
        )

        response = await recommendation_service.get_recommendations(preferences=payload)
        return response
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        # Pass the exact exception to the frontend for easy diagnosis 
        # (This is safe since it's a hobby project, and helps us trace Vercel 500s directly)
        raise HTTPException(status_code=500, detail=repr(exc)) from exc
