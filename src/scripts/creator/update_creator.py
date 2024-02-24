import argparse
from src.models.creator import update_creator
import asyncio
import warnings


async def main():
    parser = argparse.ArgumentParser(description="Update a creator in the database.")
    parser.add_argument("username", type=str, help="Creator username")
    parser.add_argument("--name", type=str, help="New creator name", default=None)
    parser.add_argument(
        "--email",
        type=str,
        help="New creator email",
    )
    parser.add_argument("--notes", type=str, help="New creator notes", default=None)

    args = parser.parse_args()

    # Collection updates into dictionary
    update_data = {}

    if args.name is not None:
        update_data["name"] = args.name
    if args.email is not None:
        update_data["email"] = args.email
    if args.notes is not None:
        update_data["notes"] = args.notes

    updated_creator = await update_creator(args.username, update_data)

    if not updated_creator:
        print("Update failed or no changes were made.")
        return

    print(f"Updated creator {updated_creator.username} to {updated_creator}")


if __name__ == "__main__":
    asyncio.run(main())
