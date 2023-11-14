from tqdm import tqdm
from loguru import logger
from src.crawler.crawler_arguments import CrawlerArguments
from src.crawler.base_crawler import BaseCrawler
from selenium.webdriver.common.by import By


class VnExpressCrawler(BaseCrawler):
    def __init__(self, arguments: CrawlerArguments, driver_type="chrome") -> None:
        super().__init__(arguments, driver_type)

    def _get_articles(self, url: str):
        return super()._get_articles(url)

    def _get_urls(self, num_pages: int):
        urls = []
        progress_bar = tqdm(
            total=len(self.arguments.available_links) * num_pages, unit=" iteration"
        )

        for link in self.arguments.available_links:
            for i in range(1, num_pages + 1):
                try:
                    url = f"{self.arguments.main_url}/{link}-p{i}"
                    self.driver.get(url)
                    title_news_tags = self.driver.find_elements(
                        by=By.CSS_SELECTOR, value="h2.title-news"
                    )
                    for tag in title_news_tags:
                        a_tag = tag.find_element(by=By.TAG_NAME, value="a")
                        urls.append(a_tag.get_attribute("href"))
                except:
                    logger.debug(f"Error at page {self.arguments.main_url}/{link}-p{i}")
            progress_bar.update(1)
        return urls
