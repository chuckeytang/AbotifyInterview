from src.models.creator import Creator, add_creator

async def generate_creator():
    await add_creator(Creator(email="first_creator@proton.me"))
    await add_creator(Creator(email="second_creator@proton.me"))
