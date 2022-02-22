from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, Message
from src.bot import dp
from loguru import logger
from src.states import States


async def register_debug_handlers():
    @dp.message_handler(
        state="*",
        commands=["redis"],
    )
    async def redis_data(message: Message, state: FSMContext):
        data = await state.get_data()
        logger.debug(f"{data}")
        await message.answer(f"redis data:\n{data}")

    # =============================

    @dp.message_handler(
        state="*",
        commands=["clear"],
    )
    async def clear_redis_data(message: Message, state: FSMContext):
        await state.reset_data()
        await message.answer("redis is empty")

    # =============================

    @dp.message_handler(
        state="*",
        commands=["state"],
    )
    async def clear_redis_data(message: Message, state: FSMContext):
        data = await state.get_state()
        await message.answer(f"current redis state:\n{data}")

    # =============================
