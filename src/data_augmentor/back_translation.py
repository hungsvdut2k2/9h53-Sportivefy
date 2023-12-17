from typing import Any, Optional

from transformers import AutoModelForSeq2SeqLM, AutoTokenizer


class Translator:
    def __init__(self, model_name: Optional[str]):
        self.model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)

    def text_normalize(self, text: Optional[str], mode: Optional[str]):
        text = text.lower()
        if mode == "vi":
            return "vi: " + text
        return "en: " + text

    def __call__(self, text: Optional[str], mode: Optional[str]) -> Any:
        text = self.text_normalize(text=text, mode=mode)
        outputs = self.model.generate(
            self.tokenizer(text, return_tensors="pt", padding=True).input_ids.to("cpu"),
            max_length=512,
        )
        return self.tokenizer.batch_decode(outputs, skip_special_tokens=True)[0]


class BackTranslation:
    def __init__(self, model_name: Optional[str]) -> None:
        self.translator = Translator(model_name=model_name)

    def __call__(self, text: Optional[str]) -> Any:
        source_translated_text = self.translator(text=text, mode="vi")
        target_translated_text = self.translator(text=source_translated_text, mode="en")
        return target_translated_text.replace("vi: ", "")


if __name__ == "__main__":
    back_translation = BackTranslation(model_name="VietAI/envit5-translation")
    print(back_translation("con chó vừa béo vừa kiêu"))
