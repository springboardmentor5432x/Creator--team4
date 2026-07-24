import certifi
from motor.motor_asyncio import AsyncIOMotorClient
from config import settings

class MongoDB:
    client: AsyncIOMotorClient = None
    db = None

db_manager = MongoDB()

async def connect_to_mongo():
    # Use TLS settings only for Atlas (mongodb+srv) connections
    connect_args = {"host": settings.MONGODB_URL}
    if settings.MONGODB_URL.startswith("mongodb+srv"):
        connect_args["tlsCAFile"] = certifi.where()
        connect_args["tlsAllowInvalidCertificates"] = True

    db_manager.client = AsyncIOMotorClient(**connect_args)
    db_manager.db = db_manager.client[settings.MONGODB_DB_NAME]
    print(f"Connected to MongoDB at {settings.MONGODB_URL}, DB: {settings.MONGODB_DB_NAME}")

async def close_mongo_connection():
    if db_manager.client:
        db_manager.client.close()
        print("MongoDB connection closed.")

def get_database():
    return db_manager.db
