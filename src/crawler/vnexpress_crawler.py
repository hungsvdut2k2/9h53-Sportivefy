from loguru import logger
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from tqdm import tqdm

from src.crawler.base_crawler import BaseCrawler
from src.crawler.crawler_arguments import CrawlerArguments
from src.utils import translate_sport


class VnExpressCrawler(BaseCrawler):
    def __init__(self, arguments: CrawlerArguments, driver_type="chrome") -> None:
        super().__init__(arguments, driver_type)

    def _get_articles(self, url_list: list):
        logger.info("Start Crawl Articles")
        result = []
        for i in tqdm(range(len(url_list))):
            try:
                corpus = {}
                self.driver.get(url_list[i])
                bread_crumb = self.driver.find_element(
                    by=By.CLASS_NAME, value="breadcrumb"
                )
                second_tag = bread_crumb.find_elements(by=By.TAG_NAME, value="li")[
                    1
                ].text.lower()
                if second_tag != "các môn khác":
                    sport_type = translate_sport(second_tag)
                else:
                    sport_type = translate_sport(
                        bread_crumb.find_elements(by=By.TAG_NAME, value="li")[
                            2
                        ].text.lower()
                    )
                corpus["title"] = self.driver.find_element(
                    by=By.CSS_SELECTOR, value="h1.title-detail"
                ).text
                corpus["sport_type"] = "education"
                article_tags = self.driver.find_elements(
                    by=By.CSS_SELECTOR, value="p.Normal"
                )
                article = [tag.text for tag in article_tags]
                if len(article) > 0:
                    corpus["author"] = article.pop()
                corpus["article"] = article
                count = 0
                image_tags = self.driver.find_elements(by=By.TAG_NAME, value="img")
                for tag in image_tags:
                    if tag.get_attribute("loading") == "lazy":
                        corpus[f"image_{count}_url"] = tag.get_attribute("data-src")
                        corpus[f"image_{count}_alt"] = tag.get_attribute("alt")
                        count += 1
                result.append(corpus)
            except NoSuchElementException:
                logger.debug("not found element")
            except TimeoutException:
                logger.debug("time out")
            except:
                logger.debug(f"Error at {url_list[i]}")
        return result

    def _get_urls(self, num_pages: int):
        urls = []
        logger.info("Start Crawl Urls")
        progress_bar = tqdm(
            total=len(self.arguments.available_links) * num_pages, unit=" iteration"
        )
        for link in self.arguments.available_links:
            for i in range(1, num_pages + 1):
                url = f"{self.arguments.main_url}/{link}-p{i}"
                try:
                    self.driver.get(url)
                    title_news_tags = self.driver.find_elements(
                        by=By.CSS_SELECTOR, value="h2.title-news"
                    )
                    for tag in title_news_tags:
                        a_tag = tag.find_element(by=By.TAG_NAME, value="a")
                        urls.append(a_tag.get_attribute("href"))
                except Exception as e:
                    logger.debug(f"Error {e} at page {url}")
                progress_bar.update(1)
        return urls
