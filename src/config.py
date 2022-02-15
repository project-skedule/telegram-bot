import re
from pathlib import Path

from jproperties import Properties

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
