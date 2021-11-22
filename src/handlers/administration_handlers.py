from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, Message
from ..text_loader import Texts
from ..api import get_canteen_timetable, get_ring_timetable
from ..bot import bot, dp
from ..keyboards import (
    ADMINISTRATION_MENU_FIRST_KEYBOARD,
    ADMINISTRATION_MENU_SECOND_KEYBOARD,
    cf,
)
from ..logger import logger
from ..some_functions import send_message
from ..states import States


async def register_administration_handlers():
    @dp.callback_query_handler(
        cf.filter(action=["administration_menu_first"]),
        state=[
            States.find_menu,
            States.find_day_of_week,
            States.administration_menu_second,
        ],
    )
    async def administration_menu_first_handler(call: CallbackQuery):
        await States.administration_menu_first.set()
        message = call.message
        await send_message(
            message,
            text="administration menu #1",
            keyboard=ADMINISTRATION_MENU_FIRST_KEYBOARD,
            parse_mode="markdown",
        )
        await call.answer()

    # =============================
    @dp.callback_query_handler(
        cf.filter(action=["administration_menu_second"]),
        state=[States.administration_menu_first],
    )
    async def administration_menu_second_handler(call: CallbackQuery):
        await States.administration_menu_second.set()
        message = call.message
        await send_message(
            message,
            text="administration menu #2",
            keyboard=ADMINISTRATION_MENU_SECOND_KEYBOARD,
            parse_mode="markdown",
        )
        await call.answer()

    # ~=============================
    @dp.callback_query_handler(
        cf.filter(action=["ring_timetable"]),
        state=[States.administration_menu_first],
    )
    async def administration_ring_timetable_handler(call: CallbackQuery):
        message = call.message
        text = await get_ring_timetable(message.chat.id)
        await send_message(
            message,
            text=text,
            keyboard=ADMINISTRATION_MENU_FIRST_KEYBOARD,
            parse_mode="markdown",
        )
        await call.answer()

    # =============================
    @dp.callback_query_handler(
        cf.filter(action=["canteen_timetable"]),
        state=[States.administration_menu_second],
    )
    async def administration_canteen_timetable_handler(call: CallbackQuery):
        message = call.message
        text = await get_canteen_timetable(message.chat.id)
        await send_message(
            message,
            text=text,
            keyboard=ADMINISTRATION_MENU_SECOND_KEYBOARD,
            parse_mode="markdown",
        )
        await call.answer()
