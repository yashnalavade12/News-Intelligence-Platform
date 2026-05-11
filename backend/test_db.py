import asyncio
from core.database import connect_db, close_db, get_db

async def test_connection():
    try:
        # Connect to MongoDB
        await connect_db()
        print("✅ MongoDB Connected Successfully")
        
        # Insert test data
        db = get_db()
        articles_collection = db["articles"]
        
        test_article = {
            "title": "Test Article",
            "url": "https://example.com/test",
            "source": "Test Source",
            "content": "This is a test article",
            "summary": "Test",
            "category": "Technology",
            "published_at": "2026-05-11T00:00:00Z"
        }
        
        result = await articles_collection.insert_one(test_article)
        print("✅ Data Inserted Successfully")
        print(f"Document ID: {result.inserted_id}")
        
        # Close connection
        await close_db()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_connection())
