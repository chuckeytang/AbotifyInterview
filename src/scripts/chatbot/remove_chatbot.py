import argparse
from src.models.chatbot import Chatbot, remove_chatbot
import asyncio
import warnings


async def main():
    parser = argparse.ArgumentParser(description="Remove a chatbot from the database.")

    parser.add_argument(
        "api_key",
        type=str,
        help="Chatbot's API key",
    )

    args = parser.parse_args()

    removed_chatbot = await remove_chatbot(args.api_key)

    if not removed_chatbot:
        print("No chatbot removed")
        return

    print(f"Removed chatbot {removed_chatbot.name} from the database.")


if __name__ == "__main__":
    asyncio.run(main())
