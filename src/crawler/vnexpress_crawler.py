from .crawler_arguments import CrawlerArguments
from .base_crawler import BaseCrawler
from selenium.webdriver.common.by import By


class VnExpressCrawler(BaseCrawler):
    def __init__(self, arguments: CrawlerArguments, driver_type="chrome") -> None:
        super().__init__(arguments, driver_type)

    def _get(self, url: str):
        self.driver.get(url)
        title_news = self.driver.find_elements(by=By.CLASS_NAME, value="title-news")
        return title_news
