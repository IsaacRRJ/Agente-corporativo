import re


def clean(text: str) -> str:
    text = re.sub(r"\t+", " ", text)
    text = re.sub(r" {2,}", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()
