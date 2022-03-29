import re
import sys
from os import getenv
from pathlib import Path

from jproperties import Properties
from loguru import logger

DEBUG = "DEBUG"
PRODUCTION = "production"
####################################################################

PROFILE = getenv("PROFILE")

####################################################################
NAME_PATTERN = re.compile(
    r"^[А-ЯЁ][а-яё]*([-][А-ЯЁ][а-яё]*)?\s*[А-ЯЁ]\.\s*[А-ЯЁ]\.\s*$"
)
####################################################################


RESOURCE_PATH = Path(__file__).parent.parent / "resources"
ANNOUNCEMENTS_PATH = RESOURCE_PATH / "announcements.json"
TEXTS_PATH = RESOURCE_PATH / "texts.toml"
UPDATE_MESSAGE_PATH = RESOURCE_PATH / "update_message.md"


TG_TEST_TOKEN = getenv("TG_TEST_TOKEN")
TG_TOKEN = getenv("TG_TOKEN")

if PROFILE == DEBUG:
    TELEGRAM_TOKEN = TG_TEST_TOKEN
elif PROFILE == PRODUCTION:
    TELEGRAM_TOKEN = TG_TOKEN
else:
    raise NameError("Unknown profile")

logger.remove()
logger.add(
    sys.stdout,
    level="TRACE",
    format="<green>{time:YYYY-MM-DDTHH:mm:ss,SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",  # format for messages
    enqueue=True,
    backtrace=True,
    colorize=True,
)

logger.add(
    "logs/telegram.log",  # filename
    level="INFO",
    mode="a",  # filemode
    rotation="50MB",  # Max file size
    format="{time:YYYY-MM-DDTHH:mm:ss,SSS} | {level:5} | {message}",  # format for messages
    enqueue=True,  # for async
    backtrace=False,
    colorize=True,
)
logger.add(
    "logs/telegram_debug.log",  # filename
    level="DEBUG",
    mode="a",  # filemode
    rotation="50MB",  # Max file size
    format="{time:YYYY-MM-DDTHH:mm:ss,SSS} | {level:5} | {message}",  # format for messages
    enqueue=True,  # for async
    backtrace=True,
    colorize=True,
)

COUNT_CABINETS_PER_PAGE = 10

API_TELEGRAM_ACCOUNT_NAME = getenv("API_TELEGRAM_ACCOUNT_NAME")
API_TELEGRAM_ACCOUNT_PASSWORD = getenv("API_TELEGRAM_ACCOUNT_PASSWORD")
URL = "http://172.0.0.7:8009"