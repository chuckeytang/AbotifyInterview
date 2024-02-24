import argparse
from src.models.creator import Creator, add_creator
import asyncio


async def main():
    parser = argparse.ArgumentParser(description="Add a creator to the database.")

    parser.add_argument(
        "--email",
        type=str,
        help="Creator email",
    )

    args = parser.parse_args()

    creator = Creator(email=args.email)

    creator = await add_creator(creator)

    if not creator:
        print("Failed to add creator to database")
        return

    print(f"Added creator {creator.email} added to the database.")


if __name__ == "__main__":
    asyncio.run(main())
