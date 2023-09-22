from abc import abstractmethod
from .crawler_arguments import CrawlerArguments
from utils import get_driver


class BaseCrawler(object):
    def __init__(self, arguments: CrawlerArguments, driver_type="chrome") -> None:
        self.arguments = arguments
        self.driver, self.wait = get_driver(driver_type).load()

    @abstractmethod
    def normalize_data(self, text: str) -> str:
        pass

    @abstractmethod
    def save_request(self, text: str) -> str:
        pass