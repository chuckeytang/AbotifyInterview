import secrets
from pymongo import MongoClient
from pymongo.server_api import ServerApi
import logging
from typing import Optional, List
from pydantic import BaseModel
from bson import ObjectId
from src.models.mongo import DatabaseClient
from pymongo.collection import ReturnDocument

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class Creator(BaseModel):
    email: str
    chatbots: List[ObjectId] = []

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: lambda oid: str(oid)}


async def add_creator(creator: Creator) -> Creator:
    creator_collection = DatabaseClient.get_collection("creators")

    result = await creator_collection.insert_one(creator.model_dump())

    creator_added = await creator_collection.find_one({"_id": result.inserted_id})

    # Return the Creator object
    return Creator(**creator_added)


async def get_creator(email: str) -> Creator:
    creator_collection = DatabaseClient.get_collection("creators")

    creator = await creator_collection.find_one({"email": email})

    if creator is None:
        print(f"Creator with email {email} not found")

    return Creator(**creator)
