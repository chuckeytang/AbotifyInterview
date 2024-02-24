import argparse
from src.models.chatbot import get_chatbot
import asyncio
import warnings


async def main():
    parser = argparse.ArgumentParser(description="Get a chatbot from database.")

    parser.add_argument(
        "api_key",
        type=str,
        help="Chatbot's API key",
    )

    args = parser.parse_args()

    chatbot = await get_chatbot(args.api_key)

    if not chatbot:
        print("No chatbot found")
        return

    print(f"Retrieved chatbot: {chatbot} ")


if __name__ == "__main__":
    asyncio.run(main())
