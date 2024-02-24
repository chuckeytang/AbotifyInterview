from fastapi.testclient import TestClient
from main import app
import pytest
from unittest.mock import patch, AsyncMock

client = TestClient(app)

VALID_EMAIL = "valid_email@gmail.com"
INVALID_EMAIL = "invalid_email@gmail.com"


async def mock_find_email(creator):
    if creator["email"] == VALID_EMAIL:
        return {"email": VALID_EMAIL}
    return None


def mock_get_collection_effect(collection_name):
    if collection_name == "extra_amazon_product_keys":
        mock_amazon_product_key_collection = AsyncMock()
        mock_amazon_product_key_collection.find_one.return_value = {
            "_id": "other_id",
            "key": "amazon test key",
        }
        mock_amazon_product_key_collection.delete_one.return_value = None
        return mock_amazon_product_key_collection
    elif collection_name == "creators":
        mock_creator_collection = AsyncMock()
        mock_creator_collection.find_one.side_effect = mock_find_email
        return mock_creator_collection

    mock_amazon_product_key_collection = AsyncMock()
    mock_amazon_product_key_collection.find_one.return_value = {
        "_id": "other_id",
        "key": "amazon test key",
    }
    mock_amazon_product_key_collection.delete_one.return_value = None
    return mock_amazon_product_key_collection


@patch("src.models.mongo.DatabaseClient.get_collection")
@pytest.mark.anyio
def test_create_chatbot_success(mock_get_collection):
    frequency = "high"
    valid_data = {
        "email": VALID_EMAIL,
        "link": "http://example.com/chatbot",
        "name": "Test Chatbot",
        "delivery_frequency": frequency,
    }

    mock_get_collection.side_effect = mock_get_collection_effect

    response = client.post("/chatbot", params=valid_data)

    assert response.status_code == 200
    assert response.json()["delivery_frequency"] == frequency
    assert response.json()["name"] == "Test Chatbot"
    assert response.json()["creator_email"] == VALID_EMAIL
    assert response.json()["prompt"] is not None


@patch("src.models.mongo.DatabaseClient.get_collection")
@pytest.mark.anyio
def test_create_chatbot_invalid_email_fail(mock_get_collection):
    invalid_email_data = {
        "email": INVALID_EMAIL,
        "link": "http://example.com/chatbot",
        "name": "Test Chatbot",
        "delivery_frequency": "high",
    }

    mock_get_collection.side_effect = mock_get_collection_effect

    response = client.post("/chatbot", params=invalid_email_data)

    assert response.status_code == 400
