from fastapi.testclient import TestClient
from main import app
import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from src.models.base import PyObjectId

client = TestClient(app)


CHATBOT_ID_1 = PyObjectId("659f01ee91729723454f00c8")
CHATBOT_ID_2 = PyObjectId("659f01ee91729234d54f00c8")

CHATBOT_API_KEY_1 = "api_key_1"
CHATBOT_API_KEY_2 = "api_key_2"
TEST_VIEW_COUNT = 10

CREATOR_ID = PyObjectId("659f01ee912397a6d54f00c8")
REVENUE_CONVERSION_RATE = 20 / 1000


def mock_count_events_effect(query):
    return TEST_VIEW_COUNT * len(query["api_key"]["$in"])


def mock_get_collection_effect(collection_name) -> AsyncMock:
    if collection_name == "creators":
        mock_creator_collection = AsyncMock()
        mock_creator_collection.find_one.return_value = {
            "chatbots": [CHATBOT_ID_1, CHATBOT_ID_2],
            "email": "test_email",
        }
        return mock_creator_collection
    elif collection_name == "chatbots":
        mock_cursor = AsyncMock()
        mock_cursor.to_list.side_effect = MagicMock(
            return_value=[
                {"api_key": CHATBOT_API_KEY_1},
                {"api_key": CHATBOT_API_KEY_2},
            ]
        )
        mock_chatbot_collection = MagicMock()
        mock_chatbot_collection.find.return_value = mock_cursor

        return mock_chatbot_collection
    elif collection_name == "api_events":
        mock_api_event_collection = AsyncMock()
        mock_api_event_collection.count_documents.side_effect = mock_count_events_effect
        return mock_api_event_collection

    mock_amazon_product_key_collection = AsyncMock()
    mock_amazon_product_key_collection.delete_one.return_value = None
    return mock_amazon_product_key_collection


@patch("src.models.mongo.DatabaseClient.get_collection")
@pytest.mark.anyio
def test_get_view_success(mock_get_collection):
    # Get views for a creator with two chatbots
    mock_get_collection.side_effect = mock_get_collection_effect

    response = client.get(f"/{CREATOR_ID}/views")

    assert response.status_code == 200
    assert response.json()["today"] == TEST_VIEW_COUNT * 2
    assert response.json()["yesterday"] == TEST_VIEW_COUNT * 2
    assert response.json()["this_month"] == TEST_VIEW_COUNT * 2
    assert response.json()["total"] == TEST_VIEW_COUNT * 2

    # Get views for a given chatbot
    response = client.get(f"/{CREATOR_ID}/views?chatbot_api_key={CHATBOT_API_KEY_1}")

    assert response.status_code == 200
    assert response.json()["today"] == TEST_VIEW_COUNT
    assert response.json()["yesterday"] == TEST_VIEW_COUNT
    assert response.json()["this_month"] == TEST_VIEW_COUNT
    assert response.json()["total"] == TEST_VIEW_COUNT


@patch("src.models.mongo.DatabaseClient.get_collection")
@pytest.mark.anyio
def test_get_revenue_success(mock_get_collection):
    # Get revenue for a creator with two chatbots
    mock_get_collection.side_effect = mock_get_collection_effect

    response = client.get(f"/{CREATOR_ID}/revenue")

    assert response.status_code == 200
    assert response.json()["today"] == TEST_VIEW_COUNT * 2 * REVENUE_CONVERSION_RATE
    assert response.json()["yesterday"] == TEST_VIEW_COUNT * 2 * REVENUE_CONVERSION_RATE
    assert (
        response.json()["this_month"] == TEST_VIEW_COUNT * 2 * REVENUE_CONVERSION_RATE
    )
    assert response.json()["total"] == TEST_VIEW_COUNT * 2 * REVENUE_CONVERSION_RATE

    # Get revenue for a given chatbot
    response = client.get(f"/{CREATOR_ID}/revenue?chatbot_api_key={CHATBOT_API_KEY_1}")
    assert response.status_code == 200
    assert response.json()["today"] == TEST_VIEW_COUNT * REVENUE_CONVERSION_RATE
    assert response.json()["yesterday"] == TEST_VIEW_COUNT * REVENUE_CONVERSION_RATE
    assert response.json()["this_month"] == TEST_VIEW_COUNT * REVENUE_CONVERSION_RATE
    assert response.json()["total"] == TEST_VIEW_COUNT * REVENUE_CONVERSION_RATE
