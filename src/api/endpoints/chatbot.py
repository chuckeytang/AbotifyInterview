from fastapi import APIRouter, HTTPException
import logging
from src.models.mongo import DatabaseClient
from src.models.chatbot import (
    ChatbotDTO,
    add_chatbot,
    chatbot_to_dto,
    Chatbot,
    remove_chatbot,
    get_chatbots,
    update_chatbot,
)
from typing import List, Dict
from bson import ObjectId

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

router = APIRouter(
    responses={404: {"description": "Not found"}},
)


@router.post("/{creator_id}/chatbot")
async def create_chatbot_route(
    creator_id: str, link: str, name: str, delivery_frequency: str
) -> ChatbotDTO:
    creator_collection = DatabaseClient.get_collection("creators")
    if await creator_collection.find_one({"_id": ObjectId(creator_id)}) is None:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to create chatbot for with error: creator id {creator_id} not found.",
        )

    chatbot_dto = await add_chatbot(
        name,
        creator_id,
        link,
        delivery_frequency,
    )

    return chatbot_dto


@router.delete("/{creator_id}/chatbot")
async def delete_chatbot_route(chatbot_api_key: str) -> None:
    await remove_chatbot(chatbot_api_key)
    return


@router.get("/{creator_id}/chatbots")
async def get_chatbots_route(creator_id: str) -> List[ChatbotDTO]:
    # change this to remove email
    """
    Get all chatbots for creator with given id
    """
    logger.info(f"Getting chatbots for creator withid: {creator_id}")
    return await get_chatbots(creator_id)


@router.put("/{creator_id}/chatbot")
async def update_chatbot_route(
    chatbot_api_key: str, fields_to_update: Dict
) -> ChatbotDTO:
    return await update_chatbot(chatbot_api_key, fields_to_update)
