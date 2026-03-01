from typing import List

from app.models.schemas import RecommendationRequest, RestaurantOut
from app.services.dataset_service import DatasetService


class RecommendationService:
    """
    Service that applies filtering and simple ranking to restaurants.

    Phase 1 logic:
    - Filter by location, price_range, minimum rating, and cuisine.
    - Sort by rating (descending).
    - Return top 10 restaurants.
    """

    def __init__(self, dataset_service: DatasetService) -> None:
        self._dataset_service = dataset_service

    async def get_recommendations(
        self, preferences: RecommendationRequest
    ) -> List[RestaurantOut]:
        # Fetch all candidate restaurants from dataset service.
        all_restaurants = await self._dataset_service.fetch_restaurants()

        # Apply filters one by one.
        filtered = [
            r
            for r in all_restaurants
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

        return results

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

        This is a very rough mapping just for the MVP.
        """
        price = restaurant.get("price")
        if price is None:
            # If we don't know the price, allow it to pass through for Phase 1.
            return True

        # Example mapping using approximate "cost for two" style numbers.
        if preferences.price_range == "low":
            return price <= 500
        if preferences.price_range == "mid":
            return 500 < price <= 1500
        if preferences.price_range == "high":
            return price > 1500

        # Should not reach here because of Pydantic validation.
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

