from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.schemas import FeedbackRequest
from app.services.repository import FeedbackRepository, RestaurantRepository


router = APIRouter(tags=["feedback"])


@router.post("/feedback")
def submit_feedback(
    payload: FeedbackRequest,
    db: Session = Depends(get_db),
) -> dict:
    """
    Store simple feedback about a restaurant from a user.
    """
    restaurant_repo = RestaurantRepository(db=db)
    feedback_repo = FeedbackRepository(db=db)

    restaurant = restaurant_repo.get_by_name(payload.restaurant_name)
    if restaurant is None:
        raise HTTPException(status_code=404, detail="Restaurant not found")

    feedback_repo.add_feedback(
        user_id=payload.user_id,
        restaurant_id=restaurant.id,
        liked=payload.liked,
    )

    return {"status": "ok"}

