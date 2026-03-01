from sqlalchemy import Boolean, Column, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

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

    feedbacks = relationship("Feedback", back_populates="restaurant")


class Feedback(Base):
    """
    Simple feedback model tying a user to a restaurant and whether they liked it.
    """

    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(String, nullable=False, index=True)
    restaurant_id = Column(Integer, ForeignKey("restaurants.id"), nullable=False)
    liked = Column(Boolean, nullable=False, default=True)

    restaurant = relationship("Restaurant", back_populates="feedbacks")

