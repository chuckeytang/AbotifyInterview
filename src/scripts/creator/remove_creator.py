import argparse
import asyncio
from src.models.creator import Creator, remove_creator


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

    await remove_creator(args.username)

    print(f"Removed creator {args.username} from database")


if __name__ == "__main__":
    asyncio.run(main())
