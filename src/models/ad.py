import numpy as np
from typing import Optional
from pydantic import BaseModel
from datetime import datetime
from src.models.mongo import DatabaseClient
from src.models.base import MongoBaseModel, PyObjectId
import logging
from src.models.chatbot import Chatbot

from typing import Optional, Dict, List
import re

import random

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class Ad(MongoBaseModel):
    source: str
    generic_product_URL: str
    description_for_chatbot: str
    full_content: str
    product_title: str
    last_time_accessed: datetime


class AdDTO(BaseModel):
    custom_product_URL: str
    description_for_chatbot: str
    full_content: str
    product_title: str


def convert_ad_to_ad_dto(ad: Ad, amazon_product_key: str) -> AdDTO:
    """
    Create an ad data transfer object that only contains information that should be returned by API
    """
    custom_product_URL = ad.generic_product_URL.replace(
        "{amazon_tracking_id}", amazon_product_key
    )

    ad_dto = AdDTO(
        custom_product_URL=custom_product_URL,
        description_for_chatbot=ad.description_for_chatbot,
        product_title=ad.product_title,
    )

    return ad_dto


# Find the top N most relevant ads
async def get_relevant_ads_by_queries(queries: List[str]) -> Optional[Dict]:
    seen_ad_ids = set()
    all_ads = []

    for query in queries:
        ads = await get_all_ads_by_query(query)
        for ad in ads:
            if ad['_id'] not in seen_ad_ids:
                all_ads.append(ad)
                seen_ad_ids.add(ad['_id'])

    most_relevant_ads = get_top_n_relevant_ads(all_ads, queries, 20)
    return most_relevant_ads

async def get_all_ads_by_query(query: str) -> Optional[Dict]:
    client = DatabaseClient()
    collection = client.get_collection("ads")
    # Convert the query into a regular expression pattern to enable a broader match
    regex_pattern = '|'.join(re.findall(r'\w+', query))

    # Construct a MongoDB query to search in 'product_title' and 'full_content' fields
    mongo_query = {
        "$or": [
            {"product_title": {"$regex": regex_pattern, "$options": "i"}},
            {"full_content": {"$regex": regex_pattern, "$options": "i"}}
        ]
    }

    # Fetching the ads from the collection that match the query
    ads = await collection.find(mongo_query).to_list(length=100)  # Limiting to 100 ads for example
    return ads
    
def calculate_weighted_relevance_score(ad: Dict, query: str, title_weight: int, content_weight: int) -> int:
    """
    Calculate the weighted relevance score of an ad based on the given query.
    Title matches are given more weight than content matches.
    
    Args:
    ad (Dict): A dictionary representing the ad.
    query (str): The search query.
    title_weight (int): The weight to give title matches.
    content_weight (int): The weight to give content matches.
    
    Returns:
    int: The relevance score of the ad.
    """
    score = 0
    query_words = set(re.findall(r'\w+', query.lower()))
    
    # Check for query words in product_title
    title_words = set(re.findall(r'\w+', ad.get('product_title', '').lower()))
    score += len(query_words.intersection(title_words)) * title_weight

    # Check for query words in full_content
    content_words = set(re.findall(r'\w+', ad.get('full_content', '').lower()))
    score += len(query_words.intersection(content_words)) * content_weight
    
    return score

def get_most_relevant_ad(ads, query, title_weight=3, content_weight=1):
    # [Interview] write your function here
    # Calucate the relevance score for each ad
    scored_ads = [(ad, calculate_weighted_relevance_score(ad, query, title_weight, content_weight)) for ad in ads]

    # Sort the ads by relevance score and return the most relevant ad
    scored_ads.sort(key=lambda x: x[1], reverse=True)
    most_relevant_ad = scored_ads[0][0] if scored_ads else None
    return most_relevant_ad

def get_top_n_relevant_ads(ads: List[Dict], queries: List[str], n=1, title_weight=3, content_weight=1) -> List[Dict]:
    """
    Get the top N most relevant ads based on the given queries.

    Args:
    ads (List[Dict]): A list of dictionaries, each representing an ad.
    queries (List[str]): A list of search queries.
    title_weight (int): The weight to give title matches.
    content_weight (int): The weight to give content matches.
    n (int): Number of top relevant ads to return.

    Returns:
    List[Dict]: A list of the top N most relevant ads.
    """
    # Initialize a dictionary to store cumulative scores for each ad
    cumulative_scores = {}

    # Calculate and accumulate scores for each ad across all queries
    for ad in ads:
        total_score = 0
        for query in queries:
            total_score += calculate_weighted_relevance_score(ad, query, title_weight, content_weight)
        cumulative_scores[ad['_id']] = (ad, total_score)

    # Sort the ads by their cumulative scores in descending order
    sorted_ads = sorted(cumulative_scores.values(), key=lambda x: x[1], reverse=True)

    # Get the top N ads based on their cumulative relevance score
    top_ads = [ad_tuple[0] for ad_tuple in sorted_ads[:n]]
    return top_ads