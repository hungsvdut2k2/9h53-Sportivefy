from abc import abstractmethod

from .driver_config import DriverConfig


class BaseDriver:
    def __init__(self, config: DriverConfig) -> None:
        self.config = config

    @abstractmethod
    def load(self):
        pass
