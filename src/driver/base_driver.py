from .driver_config import DriverConfig
from abc import abstractmethod


class BaseDriver:
    def __init__(self, config: DriverConfig) -> None:
        self.config = config

    @abstractmethod
    def load(self):
        pass
