import os

# from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()


class Mongo:
    # client = AsyncIOMotorClient(os.getenv("MONGO_URI"))
    client = MongoClient(os.getenv("MONGO_URI"))
    db = client[os.getenv("MONGO_DB")]
    user_collection = db["users"]

class JWT:
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    ALGORITHM=os.getenv("ALGORITHM")
