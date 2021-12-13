import re
from pathlib import Path

from jproperties import Properties

from src.logger import logger

logger.debug("#" * 50)
logger.debug("BOT STARTED")
logger.debug("#" * 50)

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


PROPERTIES_FILE = Path() / ".properties"
RESOURCE_PATH = Path() / "resources"
ANNOUNCEMENTS_PATH = RESOURCE_PATH / "announcements.json"
TEXTS_PATH = RESOURCE_PATH / "texts.toml"
UPDATE_MESSAGE_PATH = RESOURCE_PATH / "update_message.md"

logger.debug(f"Loading {PROPERTIES_FILE}")
with PROPERTIES_FILE.open("rb") as config_file:
    logger.debug("Loading properties file")
    properties = Properties()
    properties.load(config_file)

    logger.debug("Generating dictionary from config")
    config = {}

    for key in properties.keys():
        logger.debug(f"Loading {key} value")
        config[key] = properties[key].data

if PROFILE == DEBUG:
    logger.debug(f"Loading {DEBUG} telegram token")
    TELEGRAM_TOKEN = config["TG_TEST_TOKEN"]
elif PROFILE == PRODUCTION:
    logger.debug(f"Loading {PRODUCTION} telegram token")
    TELEGRAM_TOKEN = config["TG_TOKEN"]
else:
    logger.critical(f"Unknown profile {PROFILE}")
    raise NameError("Unknown profile")
