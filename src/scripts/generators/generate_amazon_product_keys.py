from src.scripts.get_ads.get_amazon_links import AmazonAutomator

async def generate_amazon_product_keys():
    automater = AmazonAutomator()
    await automater.add_amazon_product_keys(1,5)
