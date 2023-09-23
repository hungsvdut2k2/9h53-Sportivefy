from .crawler_arguments import CrawlerArguments
from .base_crawler import BaseCrawler
from selenium.webdriver.common.by import By


class TinTheThaoCrawler(BaseCrawler):
    def __init__(self, arguments: CrawlerArguments, driver_type="chrome") -> None:
        super().__init__(arguments, driver_type)
