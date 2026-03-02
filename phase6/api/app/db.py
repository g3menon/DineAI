import os
from motor.motor_asyncio import AsyncIOMotorClient

class DatabaseManager:
    client: AsyncIOMotorClient = None
    db = None

db_manager = DatabaseManager()

def get_db():
    if db_manager.client is None:
        url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
        db_manager.client = AsyncIOMotorClient(url)
        db_manager.db = db_manager.client.get_database("restaurant_database")
    return db_manager.db

def init_db():
    pass
