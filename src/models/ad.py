import numpy as np
from typing import Optional
from pydantic import BaseModel
from datetime import datetime
from src.models.mongo import DatabaseClient
from src.models.base import MongoBaseModel, PyObjectId
import logging
from src.models.chatbot import Chatbot

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class Ad(MongoBaseModel):
    source: str
    generic_product_URL: str
    description_for_chatbot: str
    full_content: str
    product_title: str
    last_time_accessed: datetime


class AdDTO(BaseModel):
    custom_product_URL: str
    description_for_chatbot: str
    full_content: str
    product_title: str


def convert_ad_to_ad_dto(ad: Ad, amazon_product_key: str) -> AdDTO:
    """
    Create an ad data transfer object that only contains information that should be returned by API
    """
    custom_product_URL = ad.generic_product_URL.replace(
        "{amazon_tracking_id}", amazon_product_key
    )

    ad_dto = AdDTO(
        custom_product_URL=custom_product_URL,
        description_for_chatbot=ad.description_for_chatbot,
        product_title=ad.product_title,
    )

    return ad_dto


async def get_ads() -> Optional[Ad]:
    # [Interview] write your function here
    return None
