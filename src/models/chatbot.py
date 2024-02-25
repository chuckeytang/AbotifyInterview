from enum import Enum
from pydantic import BaseModel, ValidationError
from typing import List, Dict
from src.models.mongo import DatabaseClient
from src.models.base import MongoBaseModel
import secrets
from pymongo.collection import ReturnDocument
from fastapi import HTTPException
import logging
from bson import ObjectId

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

delivery_frequency_to_prompt_dict = {
    "high": 'For EVERY user prompt in the conversation, call api.abotify.com with relevant keywords. Call the API multiple times if more than one product can be recommended. For example, when user wants to find hiking destinations, you can recommend "hiking shoes", "hiking poles", and "hiking backpacks". For example, when user asks how to keep your belongings safe, you can recommend a different product for each option you list. Always call the API before generating responses. Integrate the recommendations within the conversation as much as possible.',
    "mid": 'When the conversation is related to e-commerce products, you should call api.abotify.com with relevant keywords. Call the API multiple times if more than one product can be recommended. For example, when user wants to find hiking destinations, you can recommend "hiking shoes", "hiking poles", and "hiking backpacks". For example, when user asks how to keep your belongings safe, you can recommend a different product for each option you list. Always call the API before generating responses. Integrate the recommendations within the conversation as much as possible.',
    "low": 'When user is asking for specific product information, you should call api.abotify.com with relevant keywords. Call the API multiple times if more than one product can be recommended. For example, when user wants to find hiking destinations, you can recommend "hiking shoes", "hiking poles", and "hiking backpacks". For example, when user asks how to keep your belongings safe, you can recommend a different product for each option you list. Always call the API before generating responses. Integrate the recommendations within the conversation as much as possible.',
}


class ChatbotSource(str, Enum):
    openai_gpts = "openai_gpts"
    openai_assistant = "openai_assistant"


class DeliveryFrequency(str, Enum):
    low = "low"
    mid = "mid"
    high = "high"


class Chatbot(MongoBaseModel):
    name: str
    source: ChatbotSource
    amazon_product_key: str
    link: str
    creator_email: str
    api_key: str
    ranked_ad_ids: List[str]
    delivery_frequency: DeliveryFrequency


class ChatbotDTO(BaseModel):
    name: str
    creator_email: str
    link: str
    api_key: str
    prompt: str
    delivery_frequency: str


def chatbot_to_dto(chatbot: Chatbot) -> ChatbotDTO:
    """
    Convert a Chatbot object to a ChatbotDTO object.
    """
    delivery_frequency = "high"
    if chatbot.delivery_frequency not in delivery_frequency_to_prompt_dict:
        logger.error(
            f"Chatbot delivery frequency {chatbot.delivery_frequency} not recognized!"
        )
    else:
        delivery_frequency = chatbot.delivery_frequency

    chatbot_dto = ChatbotDTO(
        name=chatbot.name,
        link=chatbot.link,
        creator_email=chatbot.creator_email,
        api_key=chatbot.api_key,
        prompt=delivery_frequency_to_prompt_dict[delivery_frequency],
        delivery_frequency=chatbot.delivery_frequency,
    )
    return chatbot_dto


async def fetch_premade_amazon_product_key() -> str:
    amazon_product_key_collection = DatabaseClient.get_collection(
        "extra_amazon_product_keys"
    )

    amazon_product_key = await amazon_product_key_collection.find_one()

    if amazon_product_key:
        await amazon_product_key_collection.delete_one(
            {"_id": amazon_product_key["_id"]}
        )
    else:
        logger.error("Out of amazon product keys!!!")
        raise HTTPException(
            status_code=404,
            detail="Failed to retrieve Amazon Product Key, check if there are any left in database",
        )

    logger.debug(
        f"Fetched and deleted amazon product key {amazon_product_key['key']} successfully"
    )

    return amazon_product_key["key"]


async def add_chatbot(
    name: str,
    creator_id: str,
    link: str,
    ranked_ad_ids: List[str],
    delivery_frequency: str = "high",
    source=ChatbotSource.openai_gpts,
) -> ChatbotDTO:
    """
    Add chatbot to Chatbot database and to its creator
    Automatically assigns API key and amazon product key
    """
    # Verify input
    creator_collection = DatabaseClient.get_collection("creators")

    creator = await creator_collection.find_one({"email": creator_id})

    if creator is None:
        raise HTTPException(status_code=400, detail="Creator email not found.")

    # Create chatbot
    chatbot_collection = DatabaseClient.get_collection("chatbots")
    api_key = secrets.token_urlsafe()

    amazon_product_key = await fetch_premade_amazon_product_key()

    chatbot = Chatbot(
        name=name,
        source=source,
        amazon_product_key=amazon_product_key,
        ranked_ad_ids=ranked_ad_ids,
        link=link,
        creator_email=creator["email"],
        api_key=api_key,
        delivery_frequency=delivery_frequency,
    )

    # Add chatbot
    result = await chatbot_collection.insert_one(chatbot.model_dump())

    await creator_collection.find_one_and_update(
        {"email": chatbot.creator_email},
        {"$push": {"chatbots": result.inserted_id}},
    )

    return chatbot_to_dto(chatbot)


async def remove_chatbot(api_key: str) -> None:
    """
    Remove chatbot from Chatbot database by api key, and from the corresponding creator's chatbots list
    """
    # Remove chatbot from Chatbot collection
    chatbot_collection = DatabaseClient.get_collection("chatbots")
    chatbot = await chatbot_collection.find_one_and_delete({"api_key": api_key})

    if chatbot is None:
        raise HTTPException(
            status_code=400, detail=f"Chatbot with api key {api_key} is not found."
        )

    # Remove chatbot from its creator
    creator_collection = DatabaseClient.get_collection("creators")
    await creator_collection.find_one_and_update(
        {"email": chatbot["creator_email"]},
        {"$pull": {"chatbots": chatbot["_id"]}},
    )
    return


async def get_chatbots(creator_id: str) -> List[ChatbotDTO]:
    """
    Get all chatbots for a creator
    """
    chatbot_collection = DatabaseClient.get_collection("chatbots")
    creator_collection = DatabaseClient.get_collection("creators")
    creator = await creator_collection.find_one({"_id": ObjectId(creator_id)})
    if not creator:
        raise HTTPException(status_code=403)
    result = chatbot_collection.find({"creator_email": creator["email"]})

    chatbot_list = []
    async for chatbot in result:
        chatbot = Chatbot(**chatbot)
        chatbot_list.append(chatbot_to_dto(chatbot))

    return chatbot_list


async def update_chatbot(
    chatbot_api_key: str, fields_to_update: Dict[str, str]
) -> ChatbotDTO:
    # Validate input
    chatbot_collection = DatabaseClient.get_collection("chatbots")
    chatbot_dict = await chatbot_collection.find_one({"api_key": chatbot_api_key})
    if not chatbot_dict:
        raise HTTPException(status_code=404, detail="Chatbot not found")

    if "_id" in fields_to_update or "id" in fields_to_update:
        raise HTTPException(status_code=400, detail="Field not allowed")

    try:
        merged_data = {**chatbot_dict, **fields_to_update}
        Chatbot(**merged_data)
    except ValidationError as e:
        raise HTTPException(
            status_code=400, detail=f"Failed to validate input due to error: {e}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Failed to update chatbot with error {e}"
        )

    # Update chatbot
    query = {"api_key": chatbot_api_key}
    new_values = {"$set": fields_to_update}
    updated_chatbot = await chatbot_collection.find_one_and_update(
        query, new_values, return_document=ReturnDocument.AFTER
    )
    if not updated_chatbot:
        raise HTTPException(status_code=404, detail="Failed to update the chatbot")

    # Return the updated chatbot data as ChatbotDTO
    return chatbot_to_dto(Chatbot(**updated_chatbot))
