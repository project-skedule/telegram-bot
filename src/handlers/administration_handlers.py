from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, Message
from src.texts import Texts
from src.api import get_canteen_timetable, get_ring_timetable
from src.bot import bot, dp
from src.keyboards import (
    ADMINISTRATION_MENU_FIRST_KEYBOARD,
    ADMINISTRATION_MENU_SECOND_KEYBOARD,
    cf,
)
from src.logger import logger
from src.some_functions import send_message
from src.states import States


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
            text=Texts.admin_main_menu,
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
            text=Texts.admin_misc_menu,
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

        data = await get_ring_timetable(message.chat.id)
        # FIX: add break
        text = Texts.rings_timetable_header + "".join(
            Texts.rings_timetable_format.format(
                lesson_number=lsn["number"],
                time=lsn["time_start"] + " - " + lsn["time_end"],
                _break="",
            )
            for lsn in data
        )

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
        canteens = await get_canteen_timetable(message.chat.id)
        text = Texts.canteen_timetable_header + "".join(
            Texts.canteen_timetable_format.format(
                corpus_name=corpus_name, canteen_text=canteen_text
            )
            for corpus_name, canteen_text in canteens.items()
        )
        await send_message(
            message,
            text=text,
            keyboard=ADMINISTRATION_MENU_SECOND_KEYBOARD,
            parse_mode="markdown",
        )
        await call.answer()
