from aiogram.types import Update
from src.bot import dp
from src.logger import logger
from src.texts import Texts


async def register_error_handlers():
    # =================================================================
    @dp.errors_handler()
    async def global_error_handler(update: Update, exception: Exception):
        try:
            chat_id = update.message.chat.id
            username = update.message.chat.username
        except:
            chat_id = -1
            username = ""
        finally:
            logger.error(
                f"{exception.__class__.__name__}: {exception}",
                chat_id=chat_id,
                username=username,
            )
        return True
