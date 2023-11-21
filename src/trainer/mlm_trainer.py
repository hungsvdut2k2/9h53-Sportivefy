import math
import os
from transformers import (
    AutoTokenizer,
    AutoModelForMaskedLM,
    DataCollatorForLanguageModeling,
    TrainingArguments,
    Trainer,
)
from datasets import load_dataset
from loguru import logger
from src.trainer.base_trainer import BaseTrainer
from src.trainer.trainer_arguments import TrainerArguments
from src.utils import preprocess_text


class MLMTrainer(BaseTrainer):
    def __init__(self, arguments: TrainerArguments) -> None:
        super().__init__(arguments)
        self.tokenizer = AutoTokenizer.from_pretrained(self.arguments.model_name)

    def _model_init(self):
        model = AutoModelForMaskedLM.from_pretrained(self.arguments.model_name)
        return model

    def _load_dataset(self):
        dataset = load_dataset(
            "text",
            data_files={
                "train": os.path.join(self.arguments.data_directory, "train.txt"),
                "valid": os.path.join(self.arguments.data_directory, "valid.txt"),
                "test": os.path.join(self.arguments.data_directory, "test.txt"),
            },
        )
        return dataset.map(preprocess_text)

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
            warmup_steps=self.warmup_steps,
            weight_decay=self.arguments.weight_decay,
            per_device_train_batch_size=self.batch_size,
            per_device_eval_batch_size=self.batch_size,
            gradient_accumulation_steps=self.gradient_accumulation_steps,
            gradient_checkpointing=True,
            seed=42,
            fp16=True,
            push_to_hub=True,
        )
        trainer = Trainer(
            model_init=self._model_init,
            args=training_arguments,
            train_dataset=dataset["train"],
            eval_dataset=dataset["valid"],
            data_collator=data_collator,
            tokenizer=self.tokenizer,
            report_to="wandb",
        )
        trainer.train()
        eval_results = trainer.evaluate()
        logger.info(f"Perplexity: {math.exp(eval_results['eval_loss']):.2f}")
