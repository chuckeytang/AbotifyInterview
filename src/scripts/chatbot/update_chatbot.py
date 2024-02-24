import argparse
from src.models.chatbot import update_chatbot
import asyncio
import warnings


async def main():
    parser = argparse.ArgumentParser(description="Update a chatbot in the database.")
    parser.add_argument("api_key", type=str, help="API key of the Chatbot")
    parser.add_argument("--name", type=str, help="Chatbot name", default=None)
    parser.add_argument(
        "--source",
        type=str,
        help="Source of the Chatbot, e.g. openai_gpts",
        default=None,
    )
    parser.add_argument("--link", type=str, help="Chatbot link", default=None)
    parser.add_argument(
        "--description", type=str, help="Chatbot description", default=None
    )
    parser.add_argument(
        "--amazon_product_key",
        type=str,
        help="Amazon Product Key to track user purchases for the chatbot",
        default=None,
    )
    parser.add_argument(
        "--instructions", type=str, help="Chatbot instructions/prompts", default=None
    )
    parser.add_argument(
        "--returned_product_limit",
        type=int,
        help="The maximum number of products to return for each chatbot response",
        default=None,
    )

    args = parser.parse_args()

    # Verify input format
    if args.link and not args.link.startswith(("http://", "https://")):
        warnings.warn("Invalid link, link must start with http:// or https://")
        return

    # Collection updates into dictionary
    update_data = {}

    if args.name is not None:
        update_data["name"] = args.name
    if args.source is not None:
        update_data["source"] = args.source
    if args.link is not None:
        update_data["link"] = args.link
    if args.description is not None:
        update_data["description"] = args.description
    if args.instructions is not None:
        update_data["instructions"] = args.instructions
    if args.returned_product_limit is not None:
        update_data["returned_product_limit"] = args.returned_product_limit
    if args.amazon_product_key is not None:
        update_data["amazon_product_key"] = args.amazon_product_key

    updated_chatbot = await update_chatbot(args.api_key, update_data)

    if updated_chatbot is None:
        print("Update failed or no changes were made.")
        return

    print(f"Updated chatbot {updated_chatbot.name} to {updated_chatbot}")


if __name__ == "__main__":
    asyncio.run(main())
