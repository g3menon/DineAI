from fastapi import APIRouter, Depends, HTTPException

from app.db import get_db
from app.models.schemas import FeedbackRequest
from app.services.repository import FeedbackRepository, RestaurantRepository

router = APIRouter(tags=["feedback"])

@router.post("/feedback")
async def submit_feedback(
    payload: FeedbackRequest,
    db = Depends(get_db),
) -> dict:
    """
    Store simple feedback about a restaurant from a user.
    """
    restaurant_repo = RestaurantRepository(db=db)
    feedback_repo = FeedbackRepository(db=db)

    restaurant = await restaurant_repo.get_by_name(payload.restaurant_name)
    if restaurant is None:
        raise HTTPException(status_code=404, detail="Restaurant not found")

    await feedback_repo.add_feedback(
        user_id=payload.user_id,
        restaurant_id=str(restaurant.get("_id", "")),
        liked=payload.liked,
    )

    return {"status": "ok"}
