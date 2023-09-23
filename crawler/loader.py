from .crawler_arguments import CrawlerArguments
from .thethao24h_crawler import TheThao24hCrawler

crawler_type_url_mapping = {"thethao247": "https://thethao247.vn"}

url_available_list_mapping = {
    "https://thethao247.vn": [
        # "bong-da-quoc-te-c2",
        # "tin-chuyen-nhuong-c14",
        # "quan-vot-tennis-c4",
        # "vo-thuat-c228",
        # "bong-ro-c43",
        # "bong-chuyen-c45",
        # "dua-xe-c41",
        # "cau-long-c44",
        # "golf-c42",
        "chay-bo-c287",
    ]
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

    crawler_dict = {"thethao247": TheThao24hCrawler(args)}

    return crawler_dict[crawler_type]
