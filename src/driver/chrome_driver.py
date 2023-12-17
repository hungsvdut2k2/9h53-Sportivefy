from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait

from src.driver.base_driver import BaseDriver
from src.driver.driver_config import DriverConfig


class ChromeDriver(BaseDriver):
    def __init__(self, config: DriverConfig) -> None:
        super().__init__(config)

    def load(self):
        caps = {}
        caps["pageLoadStrategy"] = "none"
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.headless = self.config.is_headless
        chrome_options.set_capability("cloud:options", caps)
        driver = webdriver.Chrome(options=chrome_options)
        driver.implicitly_wait(self.config.implicitly_wait)

        wait = WebDriverWait(driver, self.config.delay_time)
        return driver, wait
