from fastapi import FastAPI
from src.api.endpoints import (
    get_product_info,
    creator,
    chatbot,
    analytics,
)

app = FastAPI()
app.include_router(get_product_info.router)
app.include_router(creator.router)
app.include_router(chatbot.router)
app.include_router(analytics.router)
