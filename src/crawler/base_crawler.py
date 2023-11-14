from abc import abstractmethod
from src.crawler.crawler_arguments import CrawlerArguments
from src.driver.driver_factory import get_driver


class BaseCrawler(object):
    def __init__(self, arguments: CrawlerArguments, driver_type="chrome") -> None:
        self.arguments = arguments
        self.driver, self.wait = get_driver(driver_type).load()

    def get_articles(self, url_list: list):
        return self._get_articles(url_list)

    def get_urls(self, num_pages: int) -> list:
        return self._get_urls(num_pages)

    @abstractmethod
    def _get_articles(self, url_list: list):
        pass

    @abstractmethod
    def _get_urls(self, num_pages: int) -> list:
        pass
