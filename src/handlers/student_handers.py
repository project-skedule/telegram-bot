from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, Message
from src.texts import Texts
from src.api import (
    get_canteen_timetable,
    get_ring_timetable,
    get_user_day_of_week,
    get_user_next_lesson,
    get_user_today,
    get_user_tomorrow,
    get_user_week,
)
from src.bot import bot, dp
from src.keyboards import (
    STUDENT_DAY_OF_WEEK_KEYBOARD,
    STUDENT_MAIN_KEYBOARD,
    STUDENT_MISC_MENU_FIRST_KEYBOARD,
    STUDENT_MISC_MENU_SECOND_KEYBOARD,
    cf,
)
from src.logger import logger
from src.some_functions import send_message
from src.states import States


async def register_student_handlers():
    @dp.callback_query_handler(
        cf.filter(action=["student_menu"]),
        state=[
            States.find_menu,
            States.find_day_of_week,
            States.student_day_of_week,
            States.student_misc_menu_first,
            States.student_misc_menu_second,
        ],
    )
    async def student_menu_handler(call: CallbackQuery):
        await States.student_menu.set()
        message = call.message
        await send_message(
            message,
            text=Texts.student_main_menu,
            keyboard=STUDENT_MAIN_KEYBOARD,
            parse_mode="markdown",
        )
        await call.answer()

    # ==============================
    @dp.callback_query_handler(
        cf.filter(action=["student_day_of_week"]),
        state=[States.student_menu],
    )
    async def student_day_of_week_handler(call: CallbackQuery):
        await States.student_day_of_week.set()
        message = call.message
        await send_message(
            message,
            text=Texts.select_day_of_week,
            keyboard=STUDENT_DAY_OF_WEEK_KEYBOARD,
            parse_mode="markdown",
        )
        await call.answer()

    # ==============================
    @dp.callback_query_handler(
        cf.filter(action=["student_choose_day_of_week"]),
        state=[States.student_day_of_week],
    )
    async def student_choose_day_of_week_handler(
        call: CallbackQuery, callback_data: dict
    ):
        await States.student_menu.set()
        message = call.message
        text = await get_user_day_of_week(
            telegram_id=message.chat.id, day_of_week=callback_data["data"], is_searching=False
        )
        await send_message(
            message,
            text=text,
            keyboard=STUDENT_MAIN_KEYBOARD,
            parse_mode="markdown",
        )
        await call.answer()

    # =============================
    @dp.callback_query_handler(
        cf.filter(action=["student_misc_menu_first"]),
        state=[States.student_menu, States.student_misc_menu_second],
    )
    async def student_misc_menu_first_handler(call: CallbackQuery, callback_data: dict):
        await States.student_misc_menu_first.set()
        message = call.message
        await send_message(
            message,
            text=Texts.student_misc_menu,
            keyboard=STUDENT_MISC_MENU_FIRST_KEYBOARD,
            parse_mode="markdown",
        )
        await call.answer()

    # =============================
    @dp.callback_query_handler(
        cf.filter(action=["student_misc_menu_second"]),
        state=[States.student_misc_menu_first],
    )
    async def student_misc_menu_second_handler(
        call: CallbackQuery, callback_data: dict
    ):
        await States.student_misc_menu_second.set()
        message = call.message
        await send_message(
            message,
            text=Texts.student_misc_menu,
            keyboard=STUDENT_MISC_MENU_SECOND_KEYBOARD,
            parse_mode="markdown",
        )
        await call.answer()

    # =============================
    @dp.callback_query_handler(
        cf.filter(action=["next_lesson"]),
        state=[States.student_menu],
    )
    async def student_next_lesson_handler(call: CallbackQuery):
        await States.student_menu.set()
        message = call.message
        # FIX format Texts.lesson_format
        text = await get_user_next_lesson(telegram_id=message.chat.id, is_searching=False)
        await send_message(
            message,
            text=text,
            keyboard=STUDENT_MAIN_KEYBOARD,
            parse_mode="markdown",
        )
        await call.answer()

    # =============================
    @dp.callback_query_handler(
        cf.filter(action=["today"]),
        state=[States.student_menu],
    )
    async def student_today_handler(call: CallbackQuery):
        await States.student_menu.set()
        message = call.message
        # TODO format
        Texts.today_timetable
        text = await get_user_today(telegram_id=message.chat.id, is_searching=True)
        await send_message(
            message,
            text=text,
            keyboard=STUDENT_MAIN_KEYBOARD,
            parse_mode="markdown",
        )
        await call.answer()

    # =============================
    @dp.callback_query_handler(
        cf.filter(action=["tomorrow"]),
        state=[States.student_menu],
    )
    async def student_tomorrow_handler(call: CallbackQuery):
        await States.student_menu.set()
        message = call.message
        # FIX format
        text = await get_user_tomorrow(telegram_id=message.chat.id, is_searching=False)
        await send_message(
            message,
            text=text,
            keyboard=STUDENT_MAIN_KEYBOARD,
            parse_mode="markdown",
        )
        await call.answer()

    # =============================
    @dp.callback_query_handler(
        cf.filter(action=["week"]),
        state=[States.student_menu],
    )
    async def student_week_handler(call: CallbackQuery):
        await States.student_menu.set()
        message = call.message
        # FIX format
        text = await get_user_week(telegram_id=message.chat.id, is_searching=False)

        await send_message(
            message,
            text=text,
            keyboard=STUDENT_MAIN_KEYBOARD,
            parse_mode="markdown",
        )
        await call.answer()

    # =============================
    @dp.callback_query_handler(
        cf.filter(action=["ring_timetable"]),
        state=[States.student_misc_menu_first],
    )
    async def student_ring_timetable_handler(call: CallbackQuery):
        await States.student_menu.set()
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
            keyboard=STUDENT_MAIN_KEYBOARD,
            parse_mode="markdown",
        )
        await call.answer()

    # =============================
    @dp.callback_query_handler(
        cf.filter(action=["canteen_timetable"]),
        state=[States.student_misc_menu_second],
    )
    async def student_canteen_timetable_handler(call: CallbackQuery):
        await States.student_menu.set()
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
            keyboard=STUDENT_MAIN_KEYBOARD,
            parse_mode="markdown",
        )
        await call.answer()
