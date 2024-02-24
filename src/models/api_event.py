from enum import Enum
from typing import List, Optional
from datetime import datetime
from src.models.mongo import DatabaseClient
from src.models.base import PyObjectId, MongoBaseModel
from pydantic import SkipValidation


class ApiType(str, Enum):
    get_product_info = "get_product_info"


class ApiEvent(MongoBaseModel):
    api_key: str
    api_type: ApiType
    input_fields: dict
    output_fields: Optional[dict] = {}
    call_receive_time: SkipValidation[datetime]
    call_end_time: Optional[SkipValidation[datetime]] = None
    error_code: Optional[int] = None
    error_details: Optional[dict] = None


async def log_api_event(api_event: ApiEvent) -> None:
    api_events_collection = DatabaseClient.get_collection("api_events")
    result = await api_events_collection.insert_one(api_event.model_dump())

    api_event = await api_events_collection.find_one({"_id": result.inserted_id})
    return ApiEvent(**api_event)
