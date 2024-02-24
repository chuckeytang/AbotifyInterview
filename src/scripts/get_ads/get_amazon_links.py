import time
from datetime import datetime
from dotenv import load_dotenv
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from openai import OpenAI
from pymongo.results import InsertOneResult
import logging
from src.models.ad import Ad
from src.scripts.utils import amazon_search_product_lines
import io
import sys
from src.models.mongo import DatabaseClient

load_dotenv()
MONGO_URL = os.getenv("MONGODB_CONNECTION_STRING")

unbuffered_stdout = io.TextIOWrapper(sys.stdout.buffer, write_through=True)

stdout_handler = logging.StreamHandler(unbuffered_stdout)
stdout_handler.setLevel(logging.DEBUG)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.addHandler(stdout_handler)


def store_link_for_amazon_search(url: str, search_keywords: str) -> InsertOneResult:
    description_for_chatbot = f"Amazon search results for '{search_keywords}'"

    ad = Ad(
        source="Amazon|associates|search_results",
        generic_product_URL=url,
        full_content="",
        product_title=description_for_chatbot,
        description_for_chatbot=description_for_chatbot,
        last_time_accessed=datetime.utcnow(),
    )
    client = MONGO_URL
    db = client["backend"]
    collection = db["ads"]
    ads_id = collection.insert_one(ad.model_dump())

    return ads_id


def enriched_description_for(search_keywords: str) -> str:
    client = OpenAI()

    completion = client.chat.completions.create(
        model="gpt-4-1106-preview",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {
                "role": "user",
                "content": f"""You are a ecommerce search keyword explainer, and given some keywords for 
            search on ecommerce websites, you write detailed explanation on what specific products might fit the 
            description, and give detailed context, especially consumer use cases and scenarios, on those products. 
            Provide the description in descriptive, straightforward, non-redundant, and informative terms. For 
            example, for the keyword “music players,” you want to describe in what scenario the consumer might use 
            this, what specific brands and products are there, what are their product specs, etc. Now, 
            give description for the keywords: '{search_keywords}'""",
            },
        ],
    )

    return completion.choices[0].message.content


class AmazonAutomator:
    def __init__(self):
        self.link_to_any_page_url = "https://affiliate-program.amazon.com/home/textlink/general?ac-ms-src=ac-nav"
        user_data_dir = f"{os.getenv('PROFILE_PATH')}/Profile"
        logger.debug("user data dir:", user_data_dir)

        options = webdriver.ChromeOptions()
        options.add_argument(f"--user-data-dir={user_data_dir}")
        options.add_argument("--silent")
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--log-level=3")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-extensions")

        # todo: enable add profile & automate login
        self.driver = webdriver.Chrome(options=options)
        logger.info("Initialized selenium driver")
        self.driver.get(self.link_to_any_page_url)
        logger.info("Retrieved amazon product page")

        if self.driver.current_url != self.link_to_any_page_url:
            try:
                amazon_email = os.getenv("AMAZON_EMAIL")
                amazon_pwd = os.getenv("AMAZON_PWD")
                logger.debug("amazon email password:", amazon_email, amazon_pwd)
                self.driver.find_element(By.ID, "ap_email").clear()
                time.sleep(1)
                self.driver.find_element(By.ID, "ap_email").send_keys(amazon_email)
                time.sleep(1)
                self.driver.find_element(By.ID, "ap_password").clear()
                time.sleep(1)
                self.driver.find_element(By.ID, "ap_password").send_keys(amazon_pwd)
                time.sleep(1)
                self.driver.find_element(By.ID, "signInSubmit").click()
                time.sleep(5)
                if "ap/cvf/request?" in self.driver.current_url:
                    logger.warn(
                        "Captcha encountered, please get base64 image from /get_screenshot "
                        "endpoint and enter the captcha at /enter_captcha endpoint. You might "
                        "need to manually login at "
                        "https://affiliate-program.amazon.com/home/textlink/general?ac-ms-src=ac-nav"
                    )

            finally:
                logger.error(
                    "Failed to retrieve Amazon Product Page. Check if Chromedriver successfully logged into Amazon"
                )

    def get_current_url(self) -> str:
        return self.driver.current_url

    def input_validate_code(self, code: str) -> str:
        self.driver.find_element(
            By.CSS_SELECTOR, "input.cvf-widget-input-code.cvf-widget-input-captcha"
        ).clear()
        time.sleep(1)
        self.driver.find_element(
            By.CSS_SELECTOR, "input.cvf-widget-input-code.cvf-widget-input-captcha"
        ).send_keys(code)
        time.sleep(1)
        self.driver.find_element(
            By.CSS_SELECTOR, "input.a-button-input.notranslate"
        ).click()
        time.sleep(3)
        return self.driver.current_url

    # next key: 101
    def add_amazon_product_keys(self, start, end) -> None:
        client = DatabaseClient()
        key_collection = client.get_collection("extra_amazon_product_keys")

        link = "https://affiliate-program.amazon.com/home/account/tag/manage"
        self.driver.get(link)

        for num in range(start, end + 1):
            self.driver.find_element(
                By.XPATH, '//*[(@id = "a-autoid-3-announce")]'
            ).click()
            product_key = "product_key_" + str(num)
            time.sleep(2)
            self.driver.find_element(By.ID, "ac-tag-create-tag_name").send_keys(
                product_key
            )
            time.sleep(1)

            # click create button
            self.driver.find_element(
                By.XPATH, '//*[(@id = "a-autoid-1-announce")]'
            ).click()
            time.sleep(3)

            # click close button
            self.driver.find_element(
                By.XPATH, '//*[(@id = "a-autoid-2-announce")]'
            ).click()
            time.sleep(3)

            key_collection.insert_one({"key": product_key + "-20"})
            time.sleep(2)
        return

    def get_link_for_amazon_search(
        self, search_keywords: str, product_line_name: str = "All Products"
    ) -> str:
        logger.debug("Getting amazon affiliate link")
        if (
            "https://affiliate-program.amazon.com/home/textlink/"
            not in self.driver.current_url
        ):
            self.driver.get(self.link_to_any_page_url)

        logger.debug("Looking for searchbar element")
        self.driver.find_element(
            By.XPATH, '//*[(@id = "textlink-search-header")]'
        ).click()
        logger.debug("Found searchbar element")

        # Given product line name, find the index of the product line in the list
        product_line_index = amazon_search_product_lines.index(product_line_name)
        # Select product from dropdown ac-textlink-search-searchIndex_code_3
        self.driver.find_element(By.XPATH, '//*[(@id = "a-autoid-6-announce")]').click()
        self.driver.find_element(
            By.ID, f"ac-textlink-search-searchIndex_code_{product_line_index}"
        ).click()

        # Enter keyword
        self.driver.find_element(By.ID, "ac-text-link-search-keyword-input").clear()
        self.driver.find_element(By.ID, "ac-text-link-search-keyword-input").send_keys(
            search_keywords
        )

        # Get today's month-date-hour string
        date_str = datetime.utcnow().strftime("%m-%d-%H")
        self.driver.find_element(By.ID, "ac-text-link-search-link-input").clear()
        self.driver.find_element(By.ID, "ac-text-link-search-link-input").send_keys(
            search_keywords + f"-{date_str}"
        )

        # Click the 'Get HTML' button
        self.driver.find_element(
            By.XPATH,
            '//input[@class="a-button-input" and @type="submit" and '
            '@aria-labelledby="a-autoid-7-announce"]',
        ).click()

        time.sleep(0.1)

        # Copy the content from the preview
        element = self.driver.find_element(By.XPATH, '//div[@class="content-view"]/a')
        link: str = element.get_attribute("href")

        return link

    def get_screenshot_as_base64(self):
        return self.driver.get_screenshot_as_base64()
