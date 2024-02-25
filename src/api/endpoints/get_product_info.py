from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from fastapi.security import APIKeyHeader
from multiprocessing import current_process
from src.models.ad import get_top_n_relevant_ads
from src.models.api_event import ApiEvent, ApiType
import logging
from typing import Optional
from src.models.mongo import DatabaseClient
from datetime import datetime
from src.models.api_event import log_api_event
from src.scripts.get_ads.get_amazon_links import AmazonAutomator
import ipaddress
from bson import ObjectId
from dotenv import load_dotenv
import os

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# AUTHORIZATION_HEADER = APIKeyHeader(name="AUTHORIZATION")
GENERIC_AMAZON_KEY = "abotify05-20"
GENERIC_AMAZON_KEY2 = "abotify-20"
OPENAI_IPS = [
    ipaddress.ip_network("23.102.140.112/28"),
    ipaddress.ip_network("13.66.11.96/28"),
    ipaddress.ip_network("104.210.133.240/28"),
]

load_dotenv()
ENVIRONMENT = os.getenv("ENVIRONMENT")


# async def get_api_key(api_key_header: str = Depends(AUTHORIZATION_HEADER)) -> str:
# Remove authorization for interview test
async def get_api_key(api_key_header: str) -> str:
    logger.info("Database client connected successfully")

    # api_key_header should be in the format of BASIC <Api Key>
    header_parts = api_key_header.split(" ")

    if len(header_parts) != 2:
        logger.error("Api key header format is unexpected:", api_key_header)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key format:" + api_key_header,
        )

    api_key = header_parts[1]
    chatbot_collection = DatabaseClient.get_collection("chatbots")

    if await chatbot_collection.find_one({"api_key": api_key}):
        logger.info("Valid API key")
        return api_key
    else:
        logger.warn(f"Invalid API key: {api_key}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key:" + api_key,
        )


async def is_api_key_valid(api_key: str) -> str:
    logger.info("Database client connected successfully")

    chatbot_collection = DatabaseClient.get_collection("chatbots")

    if not await chatbot_collection.find_one({"api_key": api_key}):
        logger.warn(f"Invalid API key: {api_key}")
        return False

    return True


router = APIRouter(
    responses={404: {"description": "Not found"}},
)

async def get_db_client():
    client = DatabaseClient()
    client.connect()
    try:
        yield client
    finally:
        await client.disconnect()

@router.get("/api/get_product_info")
async def get_product_info_with_header_route(
    request: Request, query: str, api_key: str, db_client: DatabaseClient = Depends(get_db_client)
) -> str:
    print(f"Getting product info with query: {query} and api key: {api_key}")
    logger.debug(f"Getting product info with query: {query} and api key: {api_key}")

    if not query:
        logger.error("No query provided.")
        error_message = "No query provided"

        api_event = ApiEvent(
            api_key=api_key,
            api_type=ApiType.get_product_info,
            input_fields={"query": query},
            call_receive_time=datetime.utcnow(),
            call_end_time=datetime.utcnow(),
            error_details={"detail": error_message},
        )
        await log_api_event(api_event)
        return ""

    # [Interview] This is the function to be implemented
    # Add appropriate error handling
    try:
        chatbot_collection = db_client.get_collection("chatbots")
        chatbot = await chatbot_collection.find_one({"api_key": api_key})
        if not chatbot:
            raise HTTPException(status_code=404, detail="Chatbot not found")

        # Check api_events to filter the ads already shown
        api_events_collection = db_client.get_collection("api_events")
        shown_ads = set()  # set of shown ad ids
        async for event in api_events_collection.find({"api_key": api_key}):
            shown_ad_id = event.get("output_fields", {}).get("ad_id")
            if shown_ad_id:
                shown_ads.add(shown_ad_id)
        
        #  Filter out ads that have not been shown
        ads_collection = db_client.get_collection("ads")
        ads_to_consider = []
        for ad_id in chatbot["ranked_ad_ids"]:
            if ad_id not in shown_ads:
                ad = await ads_collection.find_one({"_id": ObjectId(ad_id)})
                if ad:
                    ads_to_consider.append(ad)
                
        ad = get_top_n_relevant_ads(ads_to_consider, [query])[0]

        # Construct API event object and log it into database
        api_event = ApiEvent(
            api_key=api_key,
            api_type=ApiType.get_product_info,
            input_fields={"query": query},
            output_fields={"ad_id": str(ad["_id"])},
            call_receive_time=datetime.utcnow(),
            call_end_time=datetime.utcnow(),
            error_details={"detail": "get product info success"},
        )
        await log_api_event(api_event)
        
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

    # return product link
    return ad["generic_product_URL"]


@router.get("/test")
async def test_endpoint() -> dict:
    logger.info("Test endpoint reached")
    return {"message": "This is a test endpoint"}
