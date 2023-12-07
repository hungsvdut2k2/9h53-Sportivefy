from typing import Any, Optional
import googletrans
import translate


class Translator:
    def __init__(self, from_lang="vi", to_lang="en", method="google"):
        self.__method = method
        self.__from_lang = from_lang
        self.__to_lang = to_lang
        if method in "googletrans":
            self.translator = googletrans.Translator()
        elif method in "translate":
            self.translator = translate.Translator(from_lang=from_lang, to_lang=to_lang)

    def text_normalize(self, text: Optional[str]):
        return text.lower()

    def __call__(self, text: Optional[str]) -> Any:
        text = self.text_normalize(text)
        return (
            self.translator.translate(text)
            if self.__method in "translate"
            else self.translator.translate(text, dest=self.__to_lang).text
        )


class BackTranslation:
    def __init__(
        self, source_language: Optional[str], target_language: Optional[str]
    ) -> None:
        self.source_language_translator = Translator(
            from_lang=source_language, to_lang=target_language
        )
        self.target_language_translator = Translator(
            from_lang=target_language, to_lang=source_language
        )

    def __call__(self, text: Optional[str]) -> Any:
        source_translated_text = self.source_language_translator(text=text)
        target_translated_text = self.target_language_translator(
            text=source_translated_text
        )
        return target_translated_text


if __name__ == "__main__":
    back_translation = BackTranslation(source_language="vi", target_language="en")
    print(back_translation("con chó vừa béo vừa kiêu"))
