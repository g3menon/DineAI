from sqlalchemy import Column, Float, Integer, String

from app.db import Base


class Restaurant(Base):
    """
    ORM model for restaurants stored in the local database.
    """

    __tablename__ = "restaurants"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=False, index=True)
    location = Column(String, nullable=False, index=True)
    rating = Column(Float, nullable=False, index=True)
    price = Column(Float, nullable=True)
    cuisine = Column(String, nullable=True, index=True)

