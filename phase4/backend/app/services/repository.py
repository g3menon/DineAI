from typing import Iterable, List, Set

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.db_models import Feedback, Restaurant


class RestaurantRepository:
    """
    Simple repository for reading and writing Restaurant records.
    """

    def __init__(self, db: Session) -> None:
        self.db = db

    def count_all(self) -> int:
        return self.db.query(Restaurant).count()

    def bulk_insert_if_empty(self, rows: Iterable[dict]) -> None:
        """
        Insert all given rows into the database if there are no restaurants yet.
        """
        if self.count_all() > 0:
            return

        objects = [
            Restaurant(
                name=row["name"],
                location=row["location"],
                rating=row["rating"],
                price=row.get("price") or 0.0,
                cuisine=row.get("cuisine") or "",
            )
            for row in rows
        ]
        self.db.add_all(objects)
        self.db.commit()

    def get_all(self) -> List[Restaurant]:
        """
        Return all restaurants.
        """
        stmt = select(Restaurant)
        return list(self.db.execute(stmt).scalars().all())

    def get_by_name(self, name: str) -> Restaurant | None:
        """
        Return the first restaurant matching the given name, or None.
        """
        stmt = select(Restaurant).where(Restaurant.name == name)
        return self.db.execute(stmt).scalars().first()


class FeedbackRepository:
    """
    Repository for storing and querying user feedback.
    """

    def __init__(self, db: Session) -> None:
        self.db = db

    def add_feedback(self, user_id: str, restaurant_id: int, liked: bool) -> None:
        feedback = Feedback(user_id=user_id, restaurant_id=restaurant_id, liked=liked)
        self.db.add(feedback)
        self.db.commit()

    def get_liked_restaurant_ids(self, user_id: str) -> Set[int]:
        """
        Get IDs of restaurants the user has liked.
        """
        stmt = select(Feedback).where(Feedback.user_id == user_id, Feedback.liked.is_(True))
        rows = self.db.execute(stmt).scalars().all()
        return {fb.restaurant_id for fb in rows}

