from loguru import logger
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from tqdm import tqdm

from src.crawler.base_crawler import BaseCrawler
from src.crawler.crawler_arguments import CrawlerArguments
from src.utils import translate_sport


class DanTriCrawler(BaseCrawler):
    def __init__(self, arguments: CrawlerArguments, driver_type="chrome") -> None:
        super().__init__(arguments, driver_type)

    def _get_documents(self, url_list: list):
        result = []
        for i in tqdm(range((1650 + 678), len(url_list))):
            corpus = {}
            url = url_list[i]
            try:
                self.driver.get(url)
                bread_crumb = self.driver.find_element(
                    by=By.CLASS_NAME, value="breadcrumbs"
                )
                second_title = bread_crumb.find_elements(by=By.TAG_NAME, value="li")[
                    1
                ].text.lower()
                container = self.driver.find_element(
                    by=By.CLASS_NAME, value="singular-container"
                )
                title = container.find_element(by=By.TAG_NAME, value="h1").text
                corpus["title"] = title
                author_tag = self.driver.find_element(
                    by=By.CLASS_NAME, value="author-name"
                )
                author_a = author_tag.find_element(by=By.TAG_NAME, value="a")
                author_name = author_a.find_element(by=By.TAG_NAME, value="b").text
                if "bóng đá" in second_title:
                    sport_type = "football"
                else:
                    sport_type = translate_sport(second_title)
                corpus["sport_type"] = sport_type
                corpus["author"] = author_name

                singular_content = self.driver.find_element(
                    by=By.CLASS_NAME, value="singular-content"
                )
                content = singular_content.find_elements(by=By.TAG_NAME, value="p")
                figure_caption = singular_content.find_elements(
                    by=By.TAG_NAME, value="figcaption"
                )
                caption_list = []
                for caption in figure_caption:
                    text_caption = caption.find_element(by=By.TAG_NAME, value="p")
                    caption_list.append(text_caption.text)
                text_content = "\n".join(
                    [tag.text for tag in content if tag.text not in caption_list]
                )
                corpus["document"] = text_content
                image_tags = singular_content.find_elements(
                    by=By.CSS_SELECTOR, value="figure.image.align-center"
                )
                count = 0
                for tag in image_tags:
                    image_tag = tag.find_element(by=By.TAG_NAME, value="img")
                    title_tag = tag.find_element(by=By.TAG_NAME, value="figcaption")
                    if "cdn" in image_tag.get_attribute("data-original"):
                        corpus[f"image_{count}_url"] = image_tag.get_attribute(
                            "data-original"
                        )
                        corpus[f"image_{count}_alt"] = title_tag.find_element(
                            by=By.TAG_NAME, value="p"
                        ).text
                        count += 1
                result.append(corpus)
            except NoSuchElementException:
                logger.debug("not found element")
            except TimeoutException:
                logger.debug("time out")
            except:
                logger.debug(f"Error at {url_list[i]}")
        return result

    def _get_urls(self, num_pages: int) -> list:
        urls = []
        logger.info("Start Crawl Urls")
        progress_bar = tqdm(
            total=len(self.arguments.available_links) * num_pages, unit=" iteration"
        )
        for link in self.arguments.available_links:
            for i in range(1, num_pages + 1):
                if i == 1:
                    url = f"{self.arguments.main_url}/{link}.htm"
                else:
                    url = f"{self.arguments.main_url}/{link}/trang-{i}.htm"
                try:
                    self.driver.get(url)
                    document_titles = self.driver.find_elements(
                        by=By.CSS_SELECTOR, value="h3.article-title"
                    )
                    for tag in document_titles:
                        a_tag = tag.find_element(by=By.TAG_NAME, value="a")
                        urls.append(a_tag.get_attribute("href"))
                except:
                    logger.debug(f"Error at page {url}")
                progress_bar.update(1)
            print(urls)
        return urls
