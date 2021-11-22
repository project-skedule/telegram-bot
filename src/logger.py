from typing import Union

from loguru import logger as loguru_logger


class Logger:
    def __init__(self):
        self.logger = loguru_logger
        self.logger.add(
            "logs/misc.log",  # filename
            mode="a",  # filemode
            rotation="50MB",  # Max file size
            format="{time:DD.MM.YY HH:mm:ss} | {level} | {message}",  # format for messages
            enqueue=True,  # for async
        )
        self.logger.add(
            "logs/general.log",  # filename
            level="INFO",
            mode="a",  # filemode
            rotation="50MB",  # Max file size
            format="{time:DD.MM.YY HH:mm:ss} | {level} | {message}",  # format for messages
            enqueue=True,  # for async
        )
        self.logger.add(
            "logs/errors.log",  # filename
            level="ERROR",
            mode="a",  # filemode
            rotation="50MB",  # Max file size
            format="{time:DD.MM.YY HH:mm:ss} | {level} | {message}",  # format for messages
            enqueue=True,  # for async
        )

    def info(
        self,
        message: str,
        chat_id: int,
        username: Union[str, None],
        whoami: str,
        action: str,
    ):
        self.logger.info(f"{chat_id} | {username} | {whoami} | {action} | {message}")

    def debug(self, message: str):
        self.logger.debug(message)

    def error(self, message: str, chat_id: int, username: Union[str, None]):
        self.logger.error(f"{chat_id} | {username} | {message}")

    def critical(self, message: str):
        self.logger.critical(message)


logger = Logger()
