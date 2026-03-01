from typing import Iterable, List, Set, Optional

class RestaurantRepository:
    def __init__(self, db) -> None:
        self.collection = db.get_collection("restaurants")

    async def count_all(self) -> int:
        return await self.collection.count_documents({})

    async def bulk_insert_if_empty(self, rows: Iterable[dict]) -> None:
        if await self.count_all() > 0:
            return

        objects = [
            {
                "name": row["name"],
                "location": row["location"],
                "rating": row["rating"],
                "price": row.get("price") or 0.0,
                "cuisine": row.get("cuisine") or "",
            }
            for row in rows
        ]
        if objects:
            await self.collection.insert_many(objects)

    async def get_all(self) -> List[dict]:
        cursor = self.collection.find({})
        items = await cursor.to_list(length=None)
        return items

    async def get_by_name(self, name: str) -> Optional[dict]:
        return await self.collection.find_one({"name": name})

class FeedbackRepository:
    def __init__(self, db) -> None:
        self.collection = db.get_collection("feedback")

    async def add_feedback(self, user_id: str, restaurant_id: str, liked: bool) -> None:
        feedback = {
            "user_id": user_id, 
            "restaurant_id": restaurant_id, 
            "liked": liked
        }
        await self.collection.insert_one(feedback)

    async def get_liked_restaurant_ids(self, user_id: str) -> Set[str]:
        cursor = self.collection.find({"user_id": user_id, "liked": True})
        rows = await cursor.to_list(length=None)
        return {str(fb["restaurant_id"]) for fb in rows if "restaurant_id" in fb}
