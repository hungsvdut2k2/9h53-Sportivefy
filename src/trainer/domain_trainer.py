import os
from typing import Optional

import pandas as pd
from datasets import DatasetDict
from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
    DataCollator,
    Trainer,
    TrainingArguments,
)

from src.trainer.base_trainer import BaseTrainer
from src.trainer.trainer_arguments import TrainerArguments
from src.utils import preprocess_text


class DomainTrainer(BaseTrainer):
    def __init__(self, arguments: TrainerArguments) -> None:
        super().__init__(arguments)
        self.arguments = arguments
        self.tokenizer = AutoTokenizer.from_pretrained(self.arguments.model_name)
        self.label2id = {"in_domain": 0, "out_of_domain": 1}
        self.id2label = {0: "in_domain", 1: "out_of_domain"}

    def _process_dataset(self, type_dataset: Optional[str]):
        dataset = pd.read_csv(
            os.path.join(self.arguments.data_directory, f"{type_dataset}.csv")
        )
        dataset["text"] = dataset["text"].apply(preprocess_text)
        dataset.to_csv(
            os.path.join(self.arguments.data_directory, f"{type_dataset}.csv"),
            index=False,
        )

    def _tokenized_dataset(self, examples):
        batch_encoding = self.tokenizer(
            examples["text"],
            padding=True,
            truncation=True,
            max_length=self.arguments.max_length,
        )
        return batch_encoding

    def _load_dataset(self):
        self._process_dataset(type_dataset="train")
        self._process_dataset(type_dataset="valid")
        self._process_dataset(type_dataset="test")
        dataset_dict = DatasetDict.from_csv(
            {
                "train": os.path.join(self.arguments.data_directory, "train.csv"),
                "valid": os.path.join(self.arguments.data_directory, "valid.csv"),
                "test": os.path.join(self.arguments.data_directory, "test.csv"),
            }
        )
        dataset_dict = dataset_dict.map(self._tokenized_dataset)
        return dataset_dict

    def _model_init(self):
        return AutoModelForSequenceClassification.from_pretrained(
            pretrained_model_name_or_path=self.arguments.model_name,
            num_labels=2,
            label2id=self.label2id,
            id2label=self.id2label,
        )

    def _train(self):
        dataset = self._load_dataset()
        data_collator = DataCollator(tokenizer=self.tokenizer)
        training_arguments = TrainingArguments(
            output_dir=self.arguments.output_dir,
            evaluation_strategy="epoch",
            learning_rate=self.arguments.learning_rate,
            num_train_epochs=self.arguments.num_epochs,
            logging_dir="./logs",
            logging_steps=10,
            warmup_steps=self.arguments.warmup_steps,
            weight_decay=self.arguments.weight_decay,
            per_device_train_batch_size=self.arguments.batch_size,
            per_device_eval_batch_size=self.arguments.batch_size,
            gradient_accumulation_steps=self.arguments.gradient_accumulation_steps,
            gradient_checkpointing=True,
            seed=42,
            fp16=True,
            push_to_hub=True,
            report_to="wandb",
        )
        trainer = Trainer(
            model_init=self._model_init,
            args=training_arguments,
            train_dataset=dataset["train"],
            eval_dataset=dataset["valid"],
            data_collator=data_collator,
            tokenizer=self.tokenizer,
        )

        trainer.train()
