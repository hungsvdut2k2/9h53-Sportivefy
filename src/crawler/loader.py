from .crawler_arguments import CrawlerArguments
from .vnexpress_crawler import VnExpressCrawler
from .dantri_crawler import DanTriCrawler
from .tinthethao_crawler import TinTheThaoCrawler
from .baotintuc_crawler import BaoTinTucCrawler

crawler_type_url_mapping = {
    "vnexpress": "https://vnexpress.net/",
    "dantri": "https://dantri.com.vn/",
    "tinthethao": "https://www.tinthethao.com.vn/",
    "baotintuc": "https://baotintuc.vn/",
}

url_available_list_mapping = {
    "https://vnexpress.net/": [
        "bong-da",
        "the-thao/tennis",
        "the-thao/marathon",
        "the-thao/cac-mon-khac/dua-xe",
        "the-thao/cac-mon-khac/co-vua",
        "the-thao/cac-mon-khac/golf",
        "the-thao/cac-mon-khac/dien-kinh",
    ],
    "https://dantri.com.vn/": [
        "the-thao/bong-da-chau-au",
        "the-thao/tennis",
        "the-thao/golf",
        "the-thao/vo-thuat",
    ],
    "https://www.tinthethao.com.vn/": [
        "bong-ro",
        "bong-da-quoc-te",
        "quan-vot",
        "vo-thuat",
    ],
    "https://baotintuc.vn/": ["bong-da-547ct273", "tennis-549ct273"],
}


def convert_crawler_to_url(crawler_type: str) -> str:
    if crawler_type in crawler_type_url_mapping.keys():
        return crawler_type_url_mapping[crawler_type]
    raise ValueError("Unsupported Crawler")


def map_crawler_available_list(url: str) -> list:
    return url_available_list_mapping[url]


def get_crawler(crawler_type: str):
    main_url = convert_crawler_to_url(crawler_type)
    available_links = url_available_list_mapping[main_url]
    args = CrawlerArguments(
        connection_string="cho beo", url=main_url, available_links=available_links
    )

    crawler_dict = {
        "vnexpress": VnExpressCrawler(args),
        "dantri": DanTriCrawler(args),
        "tinthethao": TinTheThaoCrawler(args),
        "baotintuc": BaoTinTucCrawler(args),
    }

    return crawler_dict[crawler_type]
