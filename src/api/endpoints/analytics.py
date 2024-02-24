from fastapi import APIRouter
from typing import Optional
import logging
from src.models.analytics import MetricsByTime, get_chatbot_revenue, get_chatbot_views

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

router = APIRouter(
    responses={404: {"description": "Not found"}},
)


@router.get("/{creator_id}/views", response_model=MetricsByTime)
async def get_views_route(
    creator_id: str, chatbot_api_key: Optional[str] = None
) -> MetricsByTime:
    return await get_chatbot_views(creator_id, chatbot_api_key)


@router.get("/{creator_id}/revenue", response_model=MetricsByTime)
async def get_revenue_route(
    creator_id: str, chatbot_api_key: Optional[str] = None
) -> MetricsByTime:
    return await get_chatbot_revenue(creator_id, chatbot_api_key)


@router.get("/{creator_id}/balance")
async def get_balance_route(creator_id: str) -> dict:
    revenue_by_time = await get_revenue_route(creator_id)
    total_revenue = revenue_by_time.total
    return {"Total Earnings": total_revenue, "Unpaid Balance": total_revenue}
