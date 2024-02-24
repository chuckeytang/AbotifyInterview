from unittest.mock import MagicMock, patch, call, Mock
import pytest
from fastapi.testclient import TestClient
import datetime
from src.api.endpoints.get_product_info import get_product_info
from main import app
from src.models.api_event import ApiEvent, ApiType
from src.models.ad import Ad, convert_ad_to_ad_dto
import numpy as np
from src.models.base import PyObjectId
from bson import ObjectId

client = TestClient(app)

MOCK_DATETIME = datetime.datetime(2023, 12, 25, 23, 38, 19, 945688)
MOCK_AD_ID = PyObjectId("507f1f77bcf86cd799439011")
MOCK_AD = mock_ad = Ad(
    source="Example Source",
    generic_product_URL="http://example.com/{amazon_affiliate_id}product",
    description_for_chatbot="Example description",
    full_content="Full content of the ad",
    product_title="Example Product Title",
    embedding_spacy=np.array([1, 2, 3]),
    last_time_accessed=MOCK_DATETIME,
)
MOCK_AD.id = MOCK_AD_ID


@pytest.fixture
async def mock_get_ads_by_query():
    mock_ads_by_query = MagicMock()
    mock_ads_by_query.return_value = [MOCK_AD]

    return mock_ads_by_query


@pytest.fixture
def mock_update_ads_last_accessed_time():
    return MagicMock()


@pytest.fixture
def mock_log_api_event():
    return MagicMock()


# Wrapper function to return the fixed datetime value
def fixed_datetime_now():
    return MOCK_DATETIME


async def mock_update_ads_last_accessed_time(*args, **kwargs):
    pass


async def mock_log_api_event(*args, **kwargs):
    pass


@patch("src.api.get_product_info.get_amazon_product_key")
@patch("src.api.get_product_info.create_get_product_info_api_event")
@patch("src.api.get_product_info.datetime")
@patch("src.api.get_product_info.log_api_event")
@patch(
    "src.api.get_product_info.update_ads_last_accessed_time",
    side_effect=mock_update_ads_last_accessed_time,
)
@patch("src.api.get_product_info.get_ads_by_query")
def test_get_product_info_with_valid_query(
    mock_get_ads_by_query,
    mock_update_ads_last_accessed_time,
    mock_log_api_event,
    mock_datetime,
    mock_create_get_product_info_api_event,
    mock_get_amazon_product_key,
):
    # Setup
    test_query = "getelectronicrecommendations"
    test_api_key = "test_api_key"
    headers = {"apikey": test_api_key}

    SAMPLE_AMAZON_PRODUCT_KEY = "mock_amazon_product_key"
    expected_response = convert_ad_to_ad_dto(MOCK_AD, SAMPLE_AMAZON_PRODUCT_KEY)

    MOCK_API_EVENT = ApiEvent(
        id=ObjectId("658a2df586c8887b78699c3e"),
        ads_ids=[MOCK_AD_ID],
        api_key=test_api_key,
        api_type=ApiType.get_product_info,
        input_fields={"query": test_query, "api_key": test_api_key},
        output_fields=expected_response,
        call_receive_time=MOCK_DATETIME,
        call_end_time=MOCK_DATETIME,
    )

    mock_create_get_product_info_api_event.return_value = MOCK_API_EVENT
    mock_get_ads_by_query.return_value = [MOCK_AD]
    mock_update_ads_last_accessed_time.return_value = None
    mock_log_api_event.return_value = None
    mock_datetime.now.return_value = MOCK_DATETIME
    mock_get_amazon_product_key.return_value = SAMPLE_AMAZON_PRODUCT_KEY

    # Action
    response = client.get(f"/get_product_info?query={test_query}", headers=headers)

    # Verification
    assert response.status_code == 200

    response_dict = response.json()[0]
    response_dict.pop("_id")
    expected_response_dict = expected_response.model_dump(exclude={"id": True})
    assert response_dict == expected_response_dict

    mock_get_ads_by_query.assert_called_once_with(test_query, test_api_key)

    mock_update_ads_last_accessed_time.assert_called_once_with(
        [MOCK_AD_ID], MOCK_DATETIME
    )

    mock_log_api_event.assert_called_once_with(MOCK_API_EVENT)
