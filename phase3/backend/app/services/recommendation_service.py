from typing import List

from sqlalchemy.orm import Session

from app.db import get_db
from app.models.schemas import RecommendationRequest, RecommendationResponse, RestaurantOut
from app.services.dataset_service import DatasetService
from app.services.llm_service import LLMService
from app.services.repository import RestaurantRepository


class RecommendationService:
    """
    Service that applies filtering and simple ranking to restaurants, backed by a database,
    and (optionally) asks Groq LLM to generate a summary.

    Logic:
    - On first use, populate the database from the Hugging Face dataset if it's empty.
    - Load all restaurants from the database.
    - Filter by location, price_range, minimum rating, and cuisine.
    - Sort by rating (descending).
    - Return top 10 restaurants.
    - If a Groq API key is present, call the LLM to produce a short summary.
    """

    def __init__(self, dataset_service: DatasetService, db: Session) -> None:
        self._dataset_service = dataset_service
        self._db = db
        self._repository = RestaurantRepository(db=self._db)
        self._llm_service = LLMService()

    @classmethod
    async def create(cls, dataset_service: DatasetService, db: Session) -> "RecommendationService":
        """
        Factory that also ensures the database is populated at least once.
        """
        repo = RestaurantRepository(db=db)
        if repo.count_all() == 0:
            rows = await dataset_service.fetch_restaurants()
            repo.bulk_insert_if_empty(rows)
        return cls(dataset_service=dataset_service, db=db)

    async def get_recommendations(
        self, preferences: RecommendationRequest
    ) -> RecommendationResponse:
        # Load all restaurants from the database.
        all_restaurants = self._repository.get_all()

        # Convert ORM objects into simple dicts for reuse of the existing filter methods.
        candidates = [
            {
                "name": r.name,
                "location": r.location,
                "rating": r.rating,
                "price": r.price,
                "cuisine": r.cuisine,
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

        # Sort by rating, highest first.
        filtered.sort(key=lambda r: r.get("rating", 0.0), reverse=True)

        # Deduplicate by name before selecting the top N
        seen_names = set()
        deduped = []
        for r in filtered:
            name_key = r.get("name", "").strip().lower()
            if name_key not in seen_names:
                seen_names.add(name_key)
                deduped.append(r)

        top = deduped[:10]

        results: List[RestaurantOut] = []
        for r in top:
            reason_parts = ["Good rating"]
            if preferences.cuisine:
                reason_parts.append("matches your cuisine preference")
            else:
                reason_parts.append("matches your filters")

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
        """
        Simple location match: check if the user-provided location appears
        in the restaurant location string (case-insensitive).
        """
        user_loc = preferences.location.lower()
        rest_loc = str(restaurant.get("location", "")).lower()
        return user_loc in rest_loc

    def _matches_price_range(self, restaurant: dict, preferences: RecommendationRequest) -> bool:
        """
        Map a friendly price_range ('low', 'mid', 'high') to numeric bands.

        This is a very rough mapping just for this project.
        """
        price = restaurant.get("price")
        if price is None:
            # If we don't know the price, allow it to pass through for now.
            return True

        # Example mapping using approximate "cost for two" style numbers.
        if preferences.price_range == "low":
            return price <= 500
        if preferences.price_range == "mid":
            return 500 < price <= 1500
        if preferences.price_range == "high":
            return price > 1500

        # Should not reach here because of validation.
        return True

    def _matches_min_rating(self, restaurant: dict, preferences: RecommendationRequest) -> bool:
        rating = restaurant.get("rating")
        if rating is None:
            return False
        return float(rating) >= preferences.min_rating

    def _matches_cuisine(self, restaurant: dict, preferences: RecommendationRequest) -> bool:
        if not preferences.cuisine:
            # User did not specify a cuisine, so no filter here.
            return True
        target = preferences.cuisine.lower()
        restaurant_cuisine = str(restaurant.get("cuisine", "")).lower()
        return target in restaurant_cuisine

