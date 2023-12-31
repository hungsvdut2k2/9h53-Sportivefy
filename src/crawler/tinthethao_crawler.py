from loguru import logger
from selenium.webdriver.common.by import By
from tqdm import tqdm

from src.crawler.base_crawler import BaseCrawler
from src.crawler.crawler_arguments import CrawlerArguments


class TinTheThaoCrawler(BaseCrawler):
    def __init__(self, arguments: CrawlerArguments, driver_type="chrome") -> None:
        super().__init__(arguments, driver_type)

    def _get_urls(self, num_pages: int):
        urls = []
        logger.info("Start Crawl Urls")
        progress_bar = tqdm(
            total=len(self.arguments.available_links) * num_pages, unit=" iteration"
        )
        for link in self.arguments.available_links:
            for i in range(1, num_pages + 1):
                if i == 1:
                    url = f"{self.arguments.main_url}/{link}/"
                else:
                    url = f"{self.arguments.main_url}/{link}/p{i}"
                self.driver.get(url)
                pkg_tags = self.driver.find_elements(
                    by=By.CSS_SELECTOR, value="a.title_list_top_news"
                )
                for tag in pkg_tags:
                    a_tag = tag.find_element(by=By.TAG_NAME, value="a")
                    href = a_tag.get_attribute("href")
                    if href not in urls:
                        urls.append(href)
                progress_bar.update(1)
        return urls
