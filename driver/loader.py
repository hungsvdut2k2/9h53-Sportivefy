from driver.chrome_driver import ChromeDriver
from driver.driver_config import DriverConfig

driver_config = DriverConfig()
driver_mapping = {"chrome": ChromeDriver(driver_config)}


def get_driver(driver_type: str):
    if driver_type in driver_mapping.keys():
        return driver_mapping[driver_type]
    raise ValueError("Unsupported Driver")
