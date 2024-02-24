import argparse
import asyncio
from src.models.creator import Creator, get_creator


async def main():
    parser = argparse.ArgumentParser(
        description="Get a creator info from the database."
    )
    parser.add_argument(
        "username",
        type=str,
        help="Creator username",
    )

    args = parser.parse_args()

    creator = await get_creator(args.username)

    print(f"Retrieved creator {args.username}'s information: {creator}")


if __name__ == "__main__":
    asyncio.run(main())
