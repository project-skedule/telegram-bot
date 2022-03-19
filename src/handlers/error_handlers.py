from aiogram.types import Update
from loguru import logger
from src.bot import dp
from src.redis import storage
from src.texts import Texts


async def register_error_handlers():
    # =================================================================
    @dp.errors_handler()
    async def global_error_handler(update: Update, exception: Exception):
        try:
            chat_id = update.message.chat.id
            username = update.message.chat.username
            role = (await storage.get_data(chat_id)).get("role")
        except:
            chat_id = None
            username = None
            role = None
        finally:
            logger.error(
                f"{chat_id} | {username} | {role} | Error | {exception.__class__.__name__} | {exception}",
            )

        return True
