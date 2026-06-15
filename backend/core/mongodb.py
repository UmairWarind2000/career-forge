from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os
import logging

load_dotenv()
logger = logging.getLogger(__name__)

MONGO_URL = os.getenv("MONGO_URL")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME")

client = AsyncIOMotorClient(
    MONGO_URL,
    maxPoolSize=10,
    minPoolSize=2,
    connectTimeoutMS=5000,
    serverSelectionTimeoutMS=5000,
)
db = client[MONGO_DB_NAME]

async def create_indexes():
    try:
        await db["resumes"].create_index("user_id")
        await db["jobs"].create_index("title")
        await db["jobs"].create_index([("title", "text")])
        await db["gap_analyses"].create_index("user_id")
        await db["roadmaps"].create_index("user_id")
        logger.info("MongoDB indexes created successfully")
    except Exception as e:
        logger.error(f"Index creation failed: {e}")

def get_mongo_db():
    return db