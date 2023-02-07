from selenium.common.exceptions import WebDriverException
from selenium.webdriver.remote.webdriver import By
from selenium.webdriver.common.utils import Keys
import selenium.webdriver.support.expected_conditions as EC  # noqa
from selenium.webdriver.support.wait import WebDriverWait

import undetected_chromedriver as uc 
import time
from loguru import logger

class CharacterBot:
    def __init__(self, characterId):
        options = uc.ChromeOptions()
        options.headless = True
        options.add_argument( '--headless' )
        logger.trace("启动浏览器中……")
        self.driver = uc.Chrome(options=options)
        self.driver.get("https://beta.character.ai/chat?char=" + characterId)
        WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Accept')]"))).click()
        time.sleep(5)
        logger.trace("初始化完毕")
    def __del__(self):
        self.driver.close()
    def get_initial_message(self) -> str:
        msg = self.driver.find_element(By.XPATH, "//div[contains(@class, 'msg char-msg')][1]")
        return msg.text

    def send_message(self, message: str) -> str:
        # Wait until completed
        send_button = self.driver.find_element(By.XPATH, "//form/div/div/div[2]/button[1]")
        while not send_button.is_enabled():
            time.sleep(0.5)

        text_box = self.driver.find_element(By.CSS_SELECTOR, "#user-input")
        text_box.clear()
        text_box.send_keys(message, Keys.ENTER)

        while not send_button.is_enabled():
            time.sleep(0.5)

        resp = self.driver.find_element(By.XPATH, "//div[contains(@class, 'msg char-msg')][last()]")
        return resp.text
    

