from typing import Any, Dict, List

import httpx

from app.utils.parsing import parse_price, parse_rating


class DatasetService:
    """
    Service responsible for fetching and normalizing restaurant data
    from the Hugging Face dataset API.

    For Phase 1 we keep this very simple: fetch a limited number of rows
    directly from the public datasets-server API.
    """

    DATASET_API_URL = (
        "https://datasets-server.huggingface.co/rows"
        "?dataset=ManikaSaini%2Fzomato-restaurant-recommendation"
        "&config=default"
        "&split=train"
        "&limit=500"
    )

    async def fetch_restaurants(self) -> List[Dict[str, Any]]:
        """
        Fetch raw restaurant rows from the Hugging Face datasets server.

        Returns:
            A list of simplified restaurant dicts.
        """
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.get(self.DATASET_API_URL)
            response.raise_for_status()
            data = response.json()

        rows = data.get("rows", [])

        cleaned_rows: List[Dict[str, Any]] = []

        for row in rows:
            # The datasets-server usually returns each row as:
            # {"row": {...actual fields...}, "id": ..., "row_idx": ...}
            raw = row.get("row", {})

            name = str(raw.get("name") or raw.get("restaurant", "")).strip()
            location = str(raw.get("location") or raw.get("city", "")).strip()
            raw_price = raw.get("price") or raw.get("approx_cost(for two people)")
            raw_rating = raw.get("rating") or raw.get("rate")
            cuisine = str(raw.get("cuisine") or raw.get("cuisines", "")).strip()

            price = parse_price(raw_price)
            rating = parse_rating(raw_rating)

            if not name or not location or rating is None:
                # Skip incomplete rows for the simple Phase 1 MVP.
                continue

            cleaned_rows.append(
                {
                    "name": name,
                    "location": location,
                    "price": price,
                    "rating": rating,
                    "cuisine": cuisine,
                }
            )

        return cleaned_rows

