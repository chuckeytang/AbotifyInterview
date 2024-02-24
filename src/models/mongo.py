from motor.motor_asyncio import (
    AsyncIOMotorClient,
    AsyncIOMotorCollection,
    AsyncIOMotorDatabase,
)
from dotenv import load_dotenv
import certifi
from pymongo.server_api import ServerApi
import os

load_dotenv()
MONGO_URL = os.getenv("MONGODB_CONNECTION_STRING")

DATABASE_NAME = "backend"
COLLECTIONS = {"ads", "api_events", "chatbots", "creators", "dev_api_keys", "extra_amazon_product_keys"}

class DatabaseClient:
    client: AsyncIOMotorClient
    db: AsyncIOMotorDatabase

    @classmethod
    def connect(cls):
        cls.client = AsyncIOMotorClient(
            MONGO_URL, server_api=ServerApi("1"), tlsCAFile=certifi.where()
        )
        cls.db = cls.client[DATABASE_NAME]

    @classmethod
    async def disconnect(cls):
        cls.client.close()

    @classmethod
    def get_collection(cls, collection_name: str) -> AsyncIOMotorCollection:
        if collection_name not in COLLECTIONS:
            raise ValueError(f"Collection {collection_name} does not exist")
        return cls.db[collection_name]


DatabaseClient.connect()
