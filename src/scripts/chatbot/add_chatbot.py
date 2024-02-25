import argparse
from src.models.ad import get_ads_by_queries
from src.models.chatbot import Chatbot, add_chatbot
import asyncio
import warnings


async def main():
    parser = argparse.ArgumentParser(description="Add a chatbot to the database.")
    parser.add_argument("name", type=str, help="Chatbot name")
    parser.add_argument("--creator_email", type=str, help="Email of creator", required=True)
    parser.add_argument(
        "--amazon_product_key",
        type=str,
        help="Amazon product key for chatbot",
    )
    parser.add_argument(
        "--source", type=str, help="Source of the Chatbot, e.g. openai_gpts"
    )
    parser.add_argument("--link", type=str, help="Chatbot link", required=True)
    parser.add_argument(
        "--description", type=str, help="Chatbot description", default=None
    )
    parser.add_argument(
        "--instructions", type=str, help="Chatbot instructions/prompts", default=None
    )
    parser.add_argument(
        "--returned_product_limit",
        type=int,
        help="The maximum number of products to return for each chatbot response",
        default=3,
    )

    args = parser.parse_args()

    if not args.link.startswith(("http://", "https://")):
        warnings.warn("Invalid link, link must start with http:// or https://")
        return

    # chatbot = Chatbot(
    #     name=args.name,
    #     creator_id=args.creator_email,
    #     link=args.link,
    #     source=args.source,
    #     creator_username=args.creator_username,
    #     description=args.description,
    #     instructions=args.instructions,
    #     amazon_product_key=args.amazon_product_key,
    #     returned_product_limit=args.returned_product_limit,
    # )

    # fetch all the ad ids and reshuffle them before adding to the chatbot
    ranked_ad_ids = await get_ads_by_queries()

    added_chatbot = await add_chatbot(args.name, args.creator_email, args.link)

    if added_chatbot is None:
        print("Failed to add chatbot")
        return

    print(
        f"Added chatbot {added_chatbot.name} added to the database, assigned API key:{added_chatbot.api_key}"
    )


if __name__ == "__main__":
    asyncio.run(main())
