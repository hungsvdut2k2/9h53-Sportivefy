import os

from datasets import DatasetDict
from transformers import (AutoModelForMaskedLM, AutoTokenizer,
                          DataCollatorForLanguageModeling, Trainer,
                          TrainingArguments)

from src.trainer.base_trainer import BaseTrainer
from src.trainer.trainer_arguments import TrainerArguments


class MLMTrainer(BaseTrainer):
    def __init__(self, arguments: TrainerArguments) -> None:
        super().__init__(arguments)
        self.tokenizer = AutoTokenizer.from_pretrained(self.arguments.model_name)

    def _model_init(self):
        model = AutoModelForMaskedLM.from_pretrained(self.arguments.model_name)
        return model

    def _load_dataset(self):
        dataset = DatasetDict.from_csv(
            {"train": os.path.join(self.arguments.data_directory, "train.csv")}
        )
        return dataset

    def _train(self):
        self.tokenizer.pad_token = self.tokenizer.eos_token
        dataset = self._load_dataset()
        data_collator = DataCollatorForLanguageModeling(
            tokenizer=self.tokenizer,
            mlm_probability=self.arguments.mlm_proability,
            return_tensors="pt",
        )
        training_arguments = TrainingArguments(
            output_dir=self.arguments.output_dir,
            evaluation_strategy="epoch",
            learning_rate=self.arguments.learning_rate,
            num_train_epochs=self.arguments.num_epochs,
            logging_dir="./logs",
            logging_steps=100,
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
            eval_dataset=None,
            data_collator=data_collator,
            tokenizer=self.tokenizer,
        )

        trainer.train()
