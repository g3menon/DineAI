from typing import Iterable, List

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.db_models import Restaurant


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

