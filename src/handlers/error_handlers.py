from aiogram.types import Update
from src.bot import dp
from loguru import logger
from src.texts import Texts


async def register_error_handlers():
    # =================================================================
    @dp.errors_handler()
    async def global_error_handler(update: Update, exception: Exception):
        try:
            chat_id = update.message.chat.id
            username = update.message.chat.username
            logger.error(
                f"{chat_id} | {username} | {exception.__class__.__name__}: {exception}",
            )
        except:
            logger.error(
                f"{exception.__class__.__name__}: {exception}",
            )

        return True
