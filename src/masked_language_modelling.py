import argparse
import os
import wandb
from dotenv import load_dotenv
from src.trainer.trainer_arguments import TrainerArguments
from src.trainer.mlm_trainer import MLMTrainer

if __name__ == "__main__":
    load_dotenv()
    wandb_key = os.getenv("WANDB_KEY")
    wandb.login(key=wandb_key)
    os.environ["WANDB_PROJECT"] = os.getenv("WANDB_PROJECT")
    os.environ["WANDB_LOG_MODEL"] = "checkpoint"
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset-path", type=str, required=True)
    parser.add_argument("--model-name", type=str, required=True)
    parser.add_argument("--output-dir", type=str, required=True)
    parser.add_argument("--mlm-proability", type=float, default=0.15)
    parser.add_argument("--learning-rate", type=float, default=2e-5)
    parser.add_argument("--num-epochs", type=int, default=2)
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--warmup-steps", type=int, default=500)
    parser.add_argument("--gradient_accumulation_steps", type=int, default=2)
    args = parser.parse_args()
    args = vars(args)
    training_arguments = TrainerArguments(args)
    mlm_trainer = MLMTrainer(arguments=training_arguments)
    mlm_trainer.train()
