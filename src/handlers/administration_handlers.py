from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery
from src.api import get_canteen_timetable, get_free_cabinets, get_ring_timetable
from src.bot import dp
from src.keyboards import (
    ADMINISTRATION_MENU_FIRST_KEYBOARD,
    ADMINISTRATION_MENU_SECOND_KEYBOARD,
    cf,
    get_corpuses_keyboard,
)
from src.logger import logger
from src.redis import get_school_id
from src.some_functions import send_message
from src.states import States
from src.texts import Texts


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
        message = call.message
        await send_message(
            message,
            text=Texts.admin_main_menu,
            keyboard=ADMINISTRATION_MENU_FIRST_KEYBOARD,
            parse_mode="markdown",
        )

        await call.answer()
        await States.administration_menu_first.set()

    # =============================
    @dp.callback_query_handler(
        cf.filter(action=["administration_menu_second"]),
        state=[States.administration_menu_first],
    )
    async def administration_menu_second_handler(call: CallbackQuery):
        message = call.message
        await send_message(
            message,
            text=Texts.admin_misc_menu,
            keyboard=ADMINISTRATION_MENU_SECOND_KEYBOARD,
            parse_mode="markdown",
        )

        await call.answer()
        await States.administration_menu_second.set()

    # ~=============================
    @dp.callback_query_handler(
        cf.filter(action=["ring_timetable"]),
        state=[States.administration_menu_first],
    )
    async def administration_ring_timetable_handler(call: CallbackQuery):
        message = call.message

        data = await get_ring_timetable(message.chat.id)
        text = Texts.rings_timetable_header + "".join(
            Texts.rings_timetable_format.format(
                lesson_number=lsn["number"],
                time=lsn["time_start"] + " - " + lsn["time_end"],
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

    # =============================
    @dp.callback_query_handler(
        cf.filter(action=["contact_devs"]),
        state=[States.administration_menu_first],
    )
    async def administration_contact_devs(call: CallbackQuery):
        message = call.message
        text = Texts.help_message.format(telegram_id=message.chat.id)
        await send_message(
            message,
            text=text,
            keyboard=ADMINISTRATION_MENU_FIRST_KEYBOARD,
            parse_mode="markdown",
        )

        await call.answer()
        await States.administration_menu_first.set()

    # =============================
    @dp.callback_query_handler(
        cf.filter(action=["support_devs"]),
        state=[States.administration_menu_first],
    )
    async def administration_support_devs(call: CallbackQuery):
        message = call.message
        text = Texts.donate_message
        await send_message(
            message,
            text=text,
            keyboard=ADMINISTRATION_MENU_FIRST_KEYBOARD,
            parse_mode="markdown",
        )

        await call.answer()
        await States.administration_menu_first.set()

    # =============================

    @dp.callback_query_handler(
        cf.filter(action=["anouns"]),
        state=[States.administration_menu_second],
    )
    async def administration_announcements_handler(call: CallbackQuery):
        message = call.message
        text = Texts.announcements
        await send_message(
            message,
            text=text,
            keyboard=ADMINISTRATION_MENU_SECOND_KEYBOARD,
        )
        await call.answer()
        await States.administration_menu_second.set()

    @dp.callback_query_handler(
        cf.filter(action=["free_cabinets"]),
        state=[States.administration_menu_first],
    )
    async def administration_free_cabinets_handler(call: CallbackQuery):
        message = call.message
        text = Texts.free_cabinets_choose_corpuses
        await send_message(
            message,
            text=text,
            keyboard=await get_corpuses_keyboard(await get_school_id(message.chat.id)),
            parse_mode="markdown",
        )
        await call.answer()
        await States.administration_free_cabinets_corpuses.set()

    # =============================

    @dp.callback_query_handler(
        cf.filter(action=["choose_corpuses"]),
        state=[States.administration_free_cabinets_corpuses],
    )
    async def administration_free_cabinets_corpuses_handler(
        call: CallbackQuery, state: FSMContext, callback_data: dict
    ):
        message = call.message
        text = await get_free_cabinets(
            await get_school_id(message.chat.id), callback_data["data"]
        )
        await send_message(
            message,
            text=text,
            keyboard=ADMINISTRATION_MENU_FIRST_KEYBOARD,
            parse_mode="markdown",
        )
        await call.answer()
        await States.administration_menu_first.set()

    # =============================
