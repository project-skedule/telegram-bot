from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

# from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.fsm_storage.redis import RedisStorage2

from src.config import TELEGRAM_TOKEN

bot = Bot(token=TELEGRAM_TOKEN)

# For example use simple MemoryStorage for Dispatcher.

# storage = MemoryStorage()
storage = RedisStorage2("redis", 6379, db=5, pool_size=10)
dp = Dispatcher(bot, storage=storage)
