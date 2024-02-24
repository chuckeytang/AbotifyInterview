from pydantic import BaseModel
from typing import Optional
from src.models.mongo import DatabaseClient
from datetime import datetime, timedelta
import pytz
from fastapi import HTTPException
from bson import ObjectId


class MetricsByTime(BaseModel):
    today: float
    yesterday: float
    this_month: float
    total: float


async def get_views(
    creator_id: str, chatbot_api_key: Optional[str] = None
) -> MetricsByTime:
    creators_collection = DatabaseClient.get_collection("creators")
    chatbot_collection = DatabaseClient.get_collection("chatbots")
    chatbot_api_keys = []
    if chatbot_api_key is None:
        creator = await creators_collection.find_one({"_id": ObjectId(creator_id)})
        if creator is None:
            raise HTTPException(status_code=400, detail="Creator not found")
        result = chatbot_collection.find(
            {"_id": {"$in": creator["chatbots"]}}, {"api_key": 1, "_id": 0}
        )
        chatbot_api_keys = [
            dict["api_key"] for dict in await result.to_list(length=None)
        ]
    else:
        chatbot_api_keys = [chatbot_api_key]

    api_events_collection = DatabaseClient.get_collection("api_events")
    sf_tz = pytz.timezone("America/Los_Angeles")

    now_sf = datetime.now(sf_tz)

    def get_start_of_day(date):
        return sf_tz.localize(datetime(date.year, date.month, date.day))

    today_start = get_start_of_day(now_sf)
    yesterday_start = get_start_of_day(today_start - timedelta(days=1))
    yesterday_end = today_start
    this_month_start = get_start_of_day(
        datetime(today_start.year, today_start.month, 1)
    )

    today_count = await api_events_collection.count_documents(
        {
            "api_key": {"$in": chatbot_api_keys},
            "call_receive_time": {"$gte": today_start},
        }
    )

    yesterday_count = await api_events_collection.count_documents(
        {
            "api_key": {"$in": chatbot_api_keys},
            "call_receive_time": {"$gte": yesterday_start, "$lt": yesterday_end},
        }
    )

    this_month_count = await api_events_collection.count_documents(
        {
            "api_key": {"$in": chatbot_api_keys},
            "call_receive_time": {"$gte": this_month_start},
        }
    )

    total_count = await api_events_collection.count_documents(
        {"api_key": {"$in": chatbot_api_keys}}
    )

    return MetricsByTime(
        today=today_count,
        yesterday=yesterday_count,
        this_month=this_month_count,
        total=total_count,
    )


async def get_chatbot_views(
    creator_id: str, chatbot_api_key: Optional[str]
) -> MetricsByTime:
    views = await get_views(creator_id, chatbot_api_key)
    return views


def get_revenue_from_view(view_data: MetricsByTime) -> MetricsByTime:
    revenue_per_view = 0.02  # $20 / 1000 views

    def calculate_revenue(views: int):
        return round(revenue_per_view * views, 2)

    return MetricsByTime(
        today=calculate_revenue(view_data.today),
        yesterday=calculate_revenue(view_data.yesterday),
        this_month=calculate_revenue(view_data.this_month),
        total=calculate_revenue(view_data.total),
    )


async def get_chatbot_revenue(
    creator_id: str, chatbot_api_key: Optional[str]
) -> MetricsByTime:
    return MetricsByTime(
        today=0,
        yesterday=0,
        this_month=0,
        total=0,
    )

    # Uncomment the below lines when ready to enable views by chatbot
    # view_data = await get_views(creator_id, chatbot_api_key)
    # return get_revenue_from_view(view_data)
