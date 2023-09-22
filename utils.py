from driver.chrome_driver import ChromeDriver
from driver.driver_config import DriverConfig

crawler_type_url_mapping = {"thethao247": "https://thethao247.vn"}

url_available_list_mapping = {
    "https://thethao247.vn": [
        "bong-da-quoc-te-c2",
        "tin-chuyen-nhuong-c14",
        "quan-vot-tennis-c4",
        "vo-thuat-c228",
        "bong-ro-c43",
        "bong-chuyen-c45",
        "dua-xe-c41",
        "cau-long-c44",
        "golf-c42",
        "chay-bo-c287",
    ]
}

driver_config = DriverConfig()
driver_mapping = {"chrome": ChromeDriver(driver_config)}


def convert_crawler_to_url(crawler_type: str) -> str:
    if crawler_type in crawler_type_url_mapping.keys():
        return crawler_type_url_mapping[crawler_type]
    raise ValueError("Unsupported Crawler")


def map_crawler_available_list(url: str) -> list:
    return url_available_list_mapping[url]


def get_driver(driver_type: str):
    if driver_type in driver_mapping.keys():
        return driver_mapping[driver_type]
    raise ValueError("Unsupported Driver")
