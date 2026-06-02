import re
import unicodedata

def create_slug(text: str) -> str:
    text = text.lower()
    text = unicodedata.normalize("NFKD", text)

    replacements = {
        "o‘": "o", "o'": "o", "ʻo": "o", "ʼo": "o",
        "g‘": "g", "g'": "g", "ʻg": "g", "ʼg": "g",
        "’": "", "ʻ": "", "ʼ": "", "‘": "", "ʿ": ""
    }
    for old, new in replacements.items():
        text = text.replace(old, new)

    text = re.sub(r"[^a-z0-9\s-]", "", text)

    text = re.sub(r"\s+", "-", text)

    text = re.sub(r"-+", "-", text).strip("-")

    return text
