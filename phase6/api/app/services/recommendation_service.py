from typing import List

from app.models.schemas import RecommendationRequest, RecommendationResponse, RestaurantOut
from app.services.dataset_service import DatasetService
from app.services.llm_service import LLMService
from app.services.repository import FeedbackRepository, RestaurantRepository


class RecommendationService:
    def __init__(self, dataset_service: DatasetService, db) -> None:
        self._dataset_service = dataset_service
        self._db = db
        self._restaurant_repo = RestaurantRepository(db=self._db)
        self._feedback_repo = FeedbackRepository(db=self._db)
        self._llm_service = LLMService()

    @classmethod
    async def create(cls, dataset_service: DatasetService, db) -> "RecommendationService":
        """
        Factory that also ensures the database is populated at least once.
        """
        repo = RestaurantRepository(db=db)
        if await repo.count_all() == 0:
            rows = await dataset_service.fetch_restaurants()
            await repo.bulk_insert_if_empty(rows)
        return cls(dataset_service=dataset_service, db=db)

    async def get_recommendations(
        self, preferences: RecommendationRequest
    ) -> RecommendationResponse:
        # Load all restaurants from the database.
        all_restaurants = await self._restaurant_repo.get_all()

        # Determine which restaurants this user has liked before.
        liked_ids = set()
        if preferences.user_id:
            liked_ids = await self._feedback_repo.get_liked_restaurant_ids(preferences.user_id)

        # Convert ORM objects into simple dicts.
        candidates = [
            {
                "id": str(r.get("_id", "")),
                "name": r.get("name"),
                "location": r.get("location"),
                "rating": r.get("rating"),
                "price": r.get("price"),
                "cuisine": r.get("cuisine"),
            }
            for r in all_restaurants
        ]

        # Apply filters one by one.
        filtered = [
            r
            for r in candidates
            if self._matches_location(r, preferences)
            and self._matches_price_range(r, preferences)
            and self._matches_min_rating(r, preferences)
            and self._matches_cuisine(r, preferences)
        ]

        # Sort by rating, highest first, with a small boost for liked restaurants.
        def score(restaurant: dict) -> float:
            base_rating = float(restaurant.get("rating") or 0.0)
            bonus = 0.3 if restaurant.get("id") in liked_ids else 0.0
            return base_rating + bonus

        filtered.sort(key=score, reverse=True)

        # Deduplicate by name before selecting the top N
        seen_names = set()
        deduped = []
        for r in filtered:
            name_key = r["name"].strip().lower()
            if name_key not in seen_names:
                seen_names.add(name_key)
                deduped.append(r)

        top = deduped[:10]

        results: List[RestaurantOut] = []
        for r in top:
            reason_parts = ["Good rating"]
            if preferences.cuisine:
                reason_parts.append("matches your cuisine preference")
            if preferences.user_id and r.get("id") in liked_ids:
                reason_parts.append("you liked similar places before")

            reason = " and ".join(reason_parts)

            results.append(
                RestaurantOut(
                    name=r["name"],
                    location=r["location"],
                    rating=float(r.get("rating") or 0.0),
                    price=float(r.get("price") or 0.0),
                    cuisine=r.get("cuisine") or "",
                    reason=reason,
                )
            )

        llm_summary = None
        llm_used = False

        # Only call Groq if we have both results and a configured API key.
        if results and self._llm_service.is_configured():
            llm_summary = await self._llm_service.generate_summary(
                preferences=preferences,
                restaurants=results,
            )
            llm_used = llm_summary is not None

        return RecommendationResponse(
            results=results,
            llm_summary=llm_summary,
            llm_used=llm_used,
        )

    def _matches_location(self, restaurant: dict, preferences: RecommendationRequest) -> bool:
        if not preferences.location:
            return True
        user_locs = [loc.strip().lower() for loc in preferences.location.split(",") if loc.strip()]
        if not user_locs or any(ul in ["bangalore", "bengaluru", ""] for ul in user_locs):
            return True
        rest_loc = str(restaurant.get("location", "")).lower()
        for ul in user_locs:
            if ul in rest_loc or rest_loc in ul:
                return True
        return False

    def _matches_price_range(self, restaurant: dict, preferences: RecommendationRequest) -> bool:
        price = restaurant.get("price")
        if price is None:
            return True

        if preferences.price_range == "low":
            return price <= 500
        if preferences.price_range == "mid":
            return 500 < price <= 1500
        if preferences.price_range == "high":
            return price > 1500
        return True

    def _matches_min_rating(self, restaurant: dict, preferences: RecommendationRequest) -> bool:
        rating = restaurant.get("rating")
        if rating is None:
            return False
        return float(rating) >= (preferences.min_rating - 0.5)

    def _matches_cuisine(self, restaurant: dict, preferences: RecommendationRequest) -> bool:
        if not preferences.cuisine:
            return True
        target = preferences.cuisine.lower()
        restaurant_cuisine = str(restaurant.get("cuisine", "")).lower()
        return target in restaurant_cuisine

