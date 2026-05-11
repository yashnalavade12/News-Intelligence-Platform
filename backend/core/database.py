from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo import ASCENDING, DESCENDING
from core.config import get_settings

settings = get_settings()

# Global MongoDB client and database instances
client: AsyncIOMotorClient = None
db: AsyncIOMotorDatabase = None


async def connect_db():
    """Connect to MongoDB Atlas."""
    global client, db
    try:
        client = AsyncIOMotorClient(settings.MONGODB_URI)
        db = client[settings.DB_NAME]
        # Verify connection
        await db.command("ping")
        print("✅ MongoDB Connected Successfully")
    except Exception as e:
        print(f"❌ MongoDB Connection Error: {e}")
        raise


async def close_db():
    """Close MongoDB connection."""
    global client
    if client:
        client.close()
        print("✅ MongoDB Connection Closed")


async def ensure_indexes():
    """Create necessary database indexes."""
    if db is None:
        raise RuntimeError("Database not initialized")
    
    try:
        articles_collection = db["articles"]
        # Create indexes
        await articles_collection.create_index("title")
        await articles_collection.create_index("url", unique=True)
        await articles_collection.create_index([("published_at", DESCENDING)])
        await articles_collection.create_index("source")
        print("✅ Database indexes created successfully")
    except Exception as e:
        print(f"⚠️ Error creating indexes: {e}")


def get_db() -> AsyncIOMotorDatabase:
    """Get the current database instance."""
    if db is None:
        raise RuntimeError("Database not initialized. Call connect_db() first.")
    return db