from src.crawler.base_crawler import BaseCrawler
from src.crawler.crawler_arguments import CrawlerArguments
from src.crawler.vnexpress_crawler import VnExpressCrawler
from src.crawler.dantri_crawler import DanTriCrawler


def get_crawler(crawler_type: str) -> BaseCrawler:
    args = CrawlerArguments(crawler_type)
    crawler_dict = {"vnexpress": VnExpressCrawler(args), "dantri": DanTriCrawler(args)}

    return crawler_dict[crawler_type]
