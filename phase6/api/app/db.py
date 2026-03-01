import os
from motor.motor_asyncio import AsyncIOMotorClient

DATABASE_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
client = AsyncIOMotorClient(DATABASE_URL)
db = client.get_database("restaurant_database")

def get_db():
    return db

def init_db():
    pass
