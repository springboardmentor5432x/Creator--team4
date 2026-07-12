import asyncio
from datetime import datetime
from mongo.mongodb import connect_to_mongo, close_mongo_connection, get_database
from models.mongo import SOCIAL_ACCOUNTS, CONTENT_POSTS

async def main():
    await connect_to_mongo()
    db = get_database()
    
    # 1. Insert into social_accounts
    social_account = {
        "creatorId": "creator_123",
        "platform": "youtube",
        "accountId": "yt_987654321",
        "handle": "@test_creator",
        "createdAt": datetime.utcnow()
    }
    
    # 2. Insert into content_posts
    content_post = {
        "creatorId": "creator_123",
        "socialAccountId": "yt_987654321",
        "platformPostId": "vid_abc123",
        "title": "Example Video Post",
        "publishedAt": datetime.utcnow(),
        "views": 1500,
        "likes": 200
    }
    
    try:
        sa_result = await db[SOCIAL_ACCOUNTS].insert_one(social_account)
        print(f"Inserted social account into '{SOCIAL_ACCOUNTS}' with ID: {sa_result.inserted_id}")
        
        cp_result = await db[CONTENT_POSTS].insert_one(content_post)
        print(f"Inserted content post into '{CONTENT_POSTS}' with ID: {cp_result.inserted_id}")
    except Exception as e:
        print(f"Error inserting documents: {e}")
    finally:
        await close_mongo_connection()

if __name__ == "__main__":
    asyncio.run(main())
