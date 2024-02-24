from fastapi import APIRouter, HTTPException
import logging
from src.models.mongo import DatabaseClient
from src.models.creator import add_creator, Creator

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

router = APIRouter(
    responses={404: {"description": "Not found"}},
)


@router.post("/account")
async def create_account_route(email: str) -> Creator:
    logger.info(f"Creating account with email: {email}")
    creator_collection = DatabaseClient.get_collection("creators")

    if await creator_collection.find_one({"email": email}) is not None:
        raise HTTPException(
            status_code=400, detail="An user already exists with this account"
        )

    return await add_creator(Creator(email=email))
