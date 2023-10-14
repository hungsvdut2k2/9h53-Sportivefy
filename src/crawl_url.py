import argparse
import multiprocessing as mp
import logging
from tqdm import tqdm
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from tqdm import tqdm
from selenium.webdriver.common.by import By

logger = logging.getLogger(__name__)


def get_urls(url: str):
    WEB_DRIVER_DELAY_TIME = 10
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.headless = True
    driver = webdriver.Chrome(options=chrome_options)
    driver.implicitly_wait(4)
    driver.set_page_load_timeout(10)
    wait = WebDriverWait(driver, WEB_DRIVER_DELAY_TIME)

    result = []
    try:
        driver.get(url)
        title_news = driver.find_elements(by=By.CLASS_NAME, value="title-news")
        for new in title_news:
            a_tag = new.find_element(by=By.TAG_NAME, value="a")
            href = a_tag.get_attribute("href")
            if "https://c.eclick.vn" not in href:
                result.append(href)
    except:
        logger.info(f"Error with {url}")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--file-path", type=str, required=True)
    parser.add_argument("--crawler-type", default="vnexpress")
    parser.add_argument("--num-process", type=int, default=2)
    parser.add_argument("--save-directory", type=str, required=True)
    args = parser.parse_args()

    urls = open(args.file_path).readlines()
    result = []
    with mp.Pool(args.num_process) as p:
        temp_result = list(tqdm(p.imap(get_urls, urls), total=len(urls)))
        for value in temp_result:
            for url in value:
                if url not in result:
                    result.append(url)

    with open(args.save_directory, "w", encoding="utf-8") as f:
        for url in result:
            f.writelines(f"{url}\n")
