from unittest.mock import MagicMock, patch, call, Mock
import pytest
from fastapi.testclient import TestClient
import datetime
from main import app
from src.models.api_event import ApiEvent, ApiType
from src.models.ad import Ad, convert_ad_to_ad_dto
import numpy as np
from src.models.base import PyObjectId
from bson import ObjectId

from src.models.mongo import DatabaseClient
from src.scripts.generators.generate_amazon_ads import generate_amazon_ads
from src.scripts.generators.generate_amazon_product_keys import generate_amazon_product_keys
from src.scripts.generators.generate_chatbots import generate_chatbots
from src.scripts.generators.generate_creator import generate_creator

appclient = TestClient(app)
@pytest.mark.anyio
async def test_get_product_info_with_valid_query():
    # Setup
    client = DatabaseClient()
    await client.clear_all_collections()
    
    # 执行初始化脚本
    await generate_creator()
    await generate_amazon_product_keys()
    await generate_amazon_ads()
    await generate_chatbots()

    test_query = "book shelf"
    chatbots_collection = client.get_collection("chatbots")
    first_chatbot = await chatbots_collection.find_one({"name": "first_chatbot"})
    second_chatbot = await chatbots_collection.find_one({"name": "second_chatbot"})
    api_key = first_chatbot["api_key"]

    # -----------TestCase 1-----------
    # Action
    # First call the get_product_info invoking first_chatbot with query 'book shelf' 
    response = appclient.get(f"/api/get_product_info?query={test_query}&api_key={api_key}")

    # Verification
    assert response.status_code == 200
    response_data = response.json()

    # It returns the most relevant product link judging by key word mapping scores in both ad's product_title and full_content
    expected_response_data_call1 = 'https://www.amazon.com/s?k=book+shelf&crid=PLRQIKRF1L2&sprefix=book%2Caps%2C1220&ref=nb_sb_ss_ts-doa-p_1_4'
    assert response_data == expected_response_data_call1

    # -----------TestCase 2-----------
    # Action
    # Second call the get_product_info invoking first_chatbot AGAIN with query 'book shelf' 
    response = appclient.get(f"/api/get_product_info?query={test_query}&api_key={api_key}")

    # Verification
    assert response.status_code == 200
    response_data = response.json()

    # It returns the second most relevant product link judging by key word mapping scores in both ad's 
    # because the most relevant product is shown and disposed by filtering the logs in api_events
    expected_response_data_call2 = 'https://www.amazon.com/s?k=book+shelf&page=2&crid=PLRQIKRF1L2&qid=1708855530&sprefix=book%2Caps%2C1220&ref=sr_pg_2'
    assert response_data == expected_response_data_call2

    # -----------TestCase 3-----------
    # Action
    # Third call the get_product_info invoking second_chatbot with query 'book shelf' 
    api_key = second_chatbot["api_key"]
    response = appclient.get(f"/api/get_product_info?query={test_query}&api_key={api_key}")
    
    # Verification
    assert response.status_code == 200
    response_data = response.json()

    # It returns the most relevant product link again
    # because it is another chatbot of those no ads have been shown yet
    assert response_data == expected_response_data_call1

    # -----------TestCase 4-----------
    # Action
    # Fourth call the get_product_info invoking first_chatbot with query 'water flosser' 
    api_key = first_chatbot["api_key"]
    test_query = "water flosser" 
    response = appclient.get(f"/api/get_product_info?query={test_query}&api_key={api_key}")

    # Verification
    assert response.status_code == 200
    response_data = response.json()

    # For those query not having queried yet, it will work properly
    # It returns the most relevant product link judging by key word mapping scores in both ad's 
    expected_response_data_call4 = 'https://www.amazon.com/s?k=water+flosser&page=2&crid=1ZP37TP8LITX5&qid=1708855262&sprefix=%2Caps%2C699&ref=sr_pg_3'
    assert response_data == expected_response_data_call4

    # -----------TestCase 5-----------
    # Action
    # Fifth call the get_product_info invoking first_chatbot with query 'easter book' 
    # a query word it does not familiar
    api_key = first_chatbot["api_key"]
    test_query = "easter book" 
    response = appclient.get(f"/api/get_product_info?query={test_query}&api_key={api_key}")

    # Verification
    assert response.status_code == 200
    response_data = response.json()

    # It returns the book shelf ad not shown before acording to its score assess algorithm
    expected_response_data_call5 = 'https://www.amazon.com/s?k=book+shelf&page=2&crid=PLRQIKRF1L2&qid=1708855530&sprefix=book%2Caps%2C1220&ref=sr_pg_5'
    assert response_data == expected_response_data_call5
