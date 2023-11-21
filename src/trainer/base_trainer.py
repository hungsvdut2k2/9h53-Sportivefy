from abc import abstractmethod
from src.trainer.trainer_arguments import TrainerArguments


class BaseTrainer:
    def __init__(self, arguments: TrainerArguments) -> None:
        self.arguments = arguments

    def train(self):
        self._train()

    @abstractmethod
    def _train(self):
        pass
