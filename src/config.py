import re
import sys
from pathlib import Path
from jproperties import Properties
from loguru import logger

DEBUG = "DEBUG"
PRODUCTION = "production"
####################################################################

PROFILE = DEBUG
# PROFILE=PRODUCTION

####################################################################
NAME_PATTERN = re.compile(
    r"^[А-ЯЁ][а-яё]*([-][А-ЯЁ][а-яё]*)?\s*[А-ЯЁ]\.\s*[А-ЯЁ]\.\s*$"
)
####################################################################


PROPERTIES_FILE = Path(__file__).parent.parent / ".properties"
RESOURCE_PATH = Path(__file__).parent.parent / "resources"
ANNOUNCEMENTS_PATH = RESOURCE_PATH / "announcements.json"
TEXTS_PATH = RESOURCE_PATH / "texts.toml"
UPDATE_MESSAGE_PATH = RESOURCE_PATH / "update_message.md"

with PROPERTIES_FILE.open("rb") as config_file:
    properties = Properties()
    properties.load(config_file)

    config = {}

    for key in properties.keys():
        config[key] = properties[key].data

if PROFILE == DEBUG:
    TELEGRAM_TOKEN = config["TG_TEST_TOKEN"]
elif PROFILE == PRODUCTION:
    TELEGRAM_TOKEN = config["TG_TOKEN"]
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
