import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def test_simple():
    try:
        # Try without specifying database
        uri = "mongodb+srv://ynalawade1285_db_user:ynalawade1285_db_user@cluster0.tbyn8gl.mongodb.net/?retryWrites=true&w=majority"
        client = AsyncIOMotorClient(uri)
        result = await client.admin.command('ping')
        print("✅ MongoDB Connected Successfully")
        print(result)
        client.close()
    except Exception as e:
        print(f"❌ Error: {e}")

asyncio.run(test_simple())
