from .config import TEXTS_PATH
import toml


class TextFactory:
    @classmethod
    def create(cls, data):
        return type("Texts", (object,), data)


Texts = TextFactory.create(toml.load(TEXTS_PATH.open("r"))["russian"])
