import toml

from .config import TEXTS_PATH


class TextFactory:
    @classmethod
    def create(cls, data):
        return type("Texts", (object,), data)


Texts = TextFactory.create(toml.load(TEXTS_PATH.open("r", encoding="utf-8"))["russian"])
