from src.models.ad import get_relevant_ads_by_queries
from src.models.chatbot import add_chatbot

async def generate_chatbots():
    ads = await get_relevant_ads_by_queries(["water flosser", "book shelf"])
    ad_ids = [str(ad["_id"]) for ad in ads]
    await add_chatbot("first_chatbot", "first_creator@proton.me", "https://first_chatbot.com", ad_ids)

    ads = await get_relevant_ads_by_queries(["easter candy", "book shelf"])
    ad_ids = [str(ad["_id"]) for ad in ads]
    await add_chatbot("second_chatbot", "second_creator@proton.me", "https://second_chatbot.com", ad_ids)
