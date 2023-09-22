from crawler.base_crawler import BaseCrawler
from crawler.crawler_arguments import CrawlerArguments

if __name__ == "__main__":
    args = CrawlerArguments(
        connection_string="cho beo", url="cho beo", available_links=["cho beo"]
    )
    crawler = BaseCrawler(args)
    print(crawler.arguments.main_url)
