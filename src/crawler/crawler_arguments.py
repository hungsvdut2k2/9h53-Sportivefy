class CrawlerArguments:
    def __init__(self, crawler_type) -> None:
        self.args_dict = {
            "vnexpress": {
                "main_url": "https://vnexpress.net",
                "available_links": [
                    # "y-kien/thoi-su",
                    # "y-kien/doi-song",
                    # "thoi-su/dan-sinh",
                    # "thoi-su/chinh-tri"
                    # "giai-tri/gioi-sao",
                    # "giai-tri/sach",
                    # "giai-tri/phim",
                    # "giai-tri/nhac",
                    # "giai-tri/thoi-trang",
                    # "giai-tri/lam-dep",
                    # "giai-tri/san-khau-my-thuat",
                    # "giao-duc/tin-tuc",
                    # "giao-duc/tuyen-sinh",
                    # "giao-duc/chan-dung",
                    # "giao-duc/du-hoc",
                    # "giao-duc/dien-dan",
                    # "giao-duc/hoc-tieng-anh",
                    # "giao-duc/giao-duc-40"
                    # "the-gioi/tu-lieu",
                    # "the-gioi/phan-tich",
                    # "the-gioi/nguoi-viet-5-chau",
                    # "the-gioi/cuoc-song-do-day",
                    # "the-gioi/quan-su",
                    # "khoa-hoc/tin-tuc",
                    # "khoa-hoc/phat-minh",
                    # "khoa-hoc/ung-dung",
                    # "khoa-hoc/the-gioi-tu-nhien",
                    # "khoa-hoc/thuong-thuc"
                    # "bong-da",
                    "the-thao/tennis",
                    "the-thao/marathon",
                    "the-thao/cac-mon-khac",
                    "the-thao/hau-truong",
                    "the-thao/cac-mon-khac/dua-xe",
                    "the-thao/cac-mon-khac/golf",
                    "the-thao/cac-mon-khac/co-vua",
                    "the-thao/cac-mon-khac/dien-kinh",
                ],
            },
            "dantri": {
                "main_url": "https://dantri.com.vn",
                "available_links": [
                    "the-thao/bong-da-chau-au",
                    "the-thao/tennis",
                    "the-thao/golf",
                    "the-thao/vo-thuat",
                    "the-thao/hau-truong",
                    # "the-gioi/quan-su",
                    # "the-gioi/phan-tich-binh-luan",
                    # "the-gioi/the-gioi-do-day",
                    # "the-gioi/kieu-bao",
                    # "van-hoa/sach-hay",
                    # "van-hoa/doi-song-van-hoa",
                    # "van-hoa/dien-anh",
                    # "van-hoa/am-nhac",
                    # "van-hoa/hat-giong-tam-hon",
                    # "lao-dong-viec-lam/chinh-sach",
                    # "lao-dong-viec-lam/lam-giau",
                    # "lao-dong-viec-lam/chuyen-nghe",
                    # "lao-dong-viec-lam/nhan-luc-moi",
                    # "suc-manh-so/san-pham",
                ],
            },
            "tinthethao": {
                "main_url": "https://www.tinthethao.com.vn",
                "available_links": [
                    "bong-da-quoc-te",
                    "bong-ro",
                    "vo-thuat",
                    "quan-vot",
                    "hau-truong-the-thao",
                    "oto--xe-may",
                ],
            },
        }
        if crawler_type in self.args_dict.keys():
            self.main_url = self.args_dict[crawler_type]["main_url"]
            self.available_links = self.args_dict[crawler_type]["available_links"]
        else:
            raise ValueError("Unsupported Crawler")
