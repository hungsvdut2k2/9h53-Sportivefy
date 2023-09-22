from abc import abstractmethod
from .crawler_arguments import CrawlerArguments

class BaseCrawler(object):
    def __init__(self, arguments: CrawlerArguments) -> str:
        self.arguments = arguments

    @abstractmethod
    def normalize_data(self, text: str) -> str:
        pass

    @abstractmethod
    def save_request(self, text: str) -> str:
        pass