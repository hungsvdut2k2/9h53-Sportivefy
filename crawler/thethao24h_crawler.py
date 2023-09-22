from crawler.crawler_arguments import CrawlerArguments
from .base_crawler import BaseCrawler


class TheThao24hCrawler(BaseCrawler):
    def __init__(self, arguments: CrawlerArguments, driver_type="chrome") -> None:
        super().__init__(arguments, driver_type)

    """
    ul (box_latest_more) -> list li
    """

    def load_main_page(self):
        self.driver.get(self.arguments.main_url)
