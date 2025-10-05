
from logging import getLogger
import typing as t
import re


logger = getLogger(__name__)

class TextCleaner:
    """Класс для очистки текста."""
    EMOJI_PATTERN = re.compile("["
                               u"\U0001F600-\U0001F64F" u"\U0001F300-\U0001F5FF"
                               u"\U0001F680-\U0001F6FF" u"\U0001F1E0-\U0001F1FF"
                               u"\U00002500-\U00002BEF" u"\U00002702-\U000027B0"
                               u"\U000024C2-\U0001F251" u"\U0001f926-\U0001f937"
                               u"\U00010000-\U0010ffff" u"\u2640-\u2642" u"\u2600-\u2B55"
                               u"\u200d" u"\u23cf" u"\u23e9" u"\u231a" u"\ufe0f" u"\u3030"
                               "]+", flags=re.UNICODE)

    @staticmethod
    def remove_emojis(text: str) -> str:
        text = TextCleaner.EMOJI_PATTERN.sub(r'', text)
        return re.sub(r'\s+', ' ', text).strip()


class TextParser:
    """Класс для парсинга текста."""
    @staticmethod
    def tag_normalize(text: str) -> str:
        return text.lower()

    @staticmethod
    def extract_tags(text: str) -> t.Set[str]:
        # метод для поиска тэгов.
        pattern = r'\B#[\w\u0400-\u04FF]+' #r'#[\w\u0400-\u04FF]+'
        tags = re.findall(pattern, text, re.UNICODE)
        return set(TextParser.tag_normalize(tag) for tag in tags)

    @staticmethod
    def extract_title(text: str, max_length: int) -> str:
        # метод для поиска заголовков.
        first_line = text.split('\n')[0]
        if len(first_line) <= max_length:
            return TextCleaner.remove_emojis(first_line)

        # Обрезаем до последнего пробела в пределах max_length
        truncated = first_line[:max_length]
        if ' ' in truncated:
            return TextCleaner.remove_emojis(truncated[:truncated.rfind(' ')])
        return TextCleaner.remove_emojis(truncated)