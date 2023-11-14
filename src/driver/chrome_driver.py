from src.driver.base_driver import BaseDriver
from src.driver.driver_config import DriverConfig
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


class ChromeDriver(BaseDriver):
    def __init__(self, config: DriverConfig) -> None:
        super().__init__(config)

    def load(self):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.headless = self.config.is_headless
        driver = webdriver.Chrome(options=chrome_options)
        driver.implicitly_wait(self.config.implicitly_wait)

        wait = WebDriverWait(driver, self.config.delay_time)
        return driver, wait
