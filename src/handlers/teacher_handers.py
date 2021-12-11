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
    TEACHER_DAY_OF_WEEK_KEYBOARD,
    TEACHER_MAIN_KEYBOARD,
    TEACHER_MISC_MENU_FIRST_KEYBOARD,
    TEACHER_MISC_MENU_SECOND_KEYBOARD,
    cf,
)
from src.logger import logger
from src.some_functions import send_message
from src.states import States


async def register_teacher_handlers():
    @dp.callback_query_handler(
        cf.filter(action=["teacher_menu"]),
        state=[
            States.find_menu,
            States.find_day_of_week,
            States.teacher_day_of_week,
            States.teacher_misc_menu_first,
            States.teacher_misc_menu_second,
        ],
    )
    async def teacher_menu_handler(call: CallbackQuery):
        await States.teacher_menu.set()
        message = call.message
        await send_message(
            message,
            text=Texts.teacher_main_menu,
            keyboard=TEACHER_MAIN_KEYBOARD,
            parse_mode="markdown",
        )
        await call.answer()

    # ==============================
    @dp.callback_query_handler(
        cf.filter(action=["teacher_day_of_week"]),
        state=[States.teacher_menu],
    )
    async def teacher_day_of_week_handler(call: CallbackQuery):
        await States.teacher_day_of_week.set()
        message = call.message
        await send_message(
            message,
            text=Texts.select_day_of_week,
            keyboard=TEACHER_DAY_OF_WEEK_KEYBOARD,
            parse_mode="markdown",
        )
        await call.answer()

    # ==============================
    @dp.callback_query_handler(
        cf.filter(action=["teacher_choose_day_of_week"]),
        state=[States.teacher_day_of_week],
    )
    async def teacher_choose_day_of_week_handler(
        call: CallbackQuery, callback_data: dict
    ):
        await States.teacher_menu.set()
        message = call.message
        # TODO: format
        text = await get_user_day_of_week(
            telegram_id=message.chat.id,
            day_of_week=int(callback_data["data"]),
            is_searching=False,
        )
        await send_message(
            message,
            text=text,
            keyboard=TEACHER_MAIN_KEYBOARD,
            parse_mode="markdown",
        )
        await call.answer()

    # =============================
    @dp.callback_query_handler(
        cf.filter(action=["teacher_misc_menu_first"]),
        state=[States.teacher_menu, States.teacher_misc_menu_second],
    )
    async def teacher_misc_menu_first_handler(call: CallbackQuery, callback_data: dict):
        await States.teacher_misc_menu_first.set()
        message = call.message
        await send_message(
            message,
            text=Texts.teacher_misc_menu,
            keyboard=TEACHER_MISC_MENU_FIRST_KEYBOARD,
            parse_mode="markdown",
        )
        await call.answer()

    # =============================

    @dp.callback_query_handler(
        cf.filter(action=["teacher_misc_menu_second"]),
        state=[States.teacher_menu, States.teacher_misc_menu_first],
    )
    async def teacher_misc_menu_second_handler(
        call: CallbackQuery, callback_data: dict
    ):
        await States.teacher_misc_menu_second.set()
        message = call.message
        await send_message(
            message,
            text=Texts.teacher_misc_menu,
            keyboard=TEACHER_MISC_MENU_SECOND_KEYBOARD,
            parse_mode="markdown",
        )
        await call.answer()

    # =============================
    @dp.callback_query_handler(
        cf.filter(action=["next_lesson"]),
        state=[States.teacher_menu],
    )
    async def teacher_next_lesson_handler(call: CallbackQuery):
        message = call.message
        # FIX: format
        text = await get_user_next_lesson(
            telegram_id=message.chat.id, is_searching=False
        )
        await send_message(
            message,
            text=text,
            keyboard=TEACHER_MAIN_KEYBOARD,
            parse_mode="markdown",
        )
        await call.answer()

    # =============================
    @dp.callback_query_handler(
        cf.filter(action=["today"]),
        state=[States.teacher_menu],
    )
    async def teacher_today_handler(call: CallbackQuery):
        message = call.message
        # FIX: format
        text = await get_user_today(telegram_id=message.chat.id, is_searching=False)
        await send_message(
            message,
            text=text,
            keyboard=TEACHER_MAIN_KEYBOARD,
            parse_mode="markdown",
        )
        await call.answer()

    # =============================
    @dp.callback_query_handler(
        cf.filter(action=["tomorrow"]),
        state=[States.teacher_menu],
    )
    async def teacher_tomorrow_handler(call: CallbackQuery):
        message = call.message
        # FIX: format
        text = await get_user_tomorrow(telegram_id=message.chat.id, is_searching=False)
        await send_message(
            message,
            text=text,
            keyboard=TEACHER_MAIN_KEYBOARD,
            parse_mode="markdown",
        )
        await call.answer()

    # =============================
    @dp.callback_query_handler(
        cf.filter(action=["week"]),
        state=[States.teacher_menu],
    )
    async def teacher_week_handler(call: CallbackQuery):
        message = call.message
        # FIX: format
        text = await get_user_week(telegram_id=message.chat.id, is_searching=False)
        await send_message(
            message,
            text=text,
            keyboard=TEACHER_MAIN_KEYBOARD,
            parse_mode="markdown",
        )
        await call.answer()

    # =============================
    @dp.callback_query_handler(
        cf.filter(action=["ring_timetable"]),
        state=[States.teacher_misc_menu_first],
    )
    async def student_ring_timetable_handler(call: CallbackQuery):
        await States.teacher_menu.set()
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
            keyboard=TEACHER_MAIN_KEYBOARD,
            parse_mode="markdown",
        )
        await call.answer()

    # =============================
    @dp.callback_query_handler(
        cf.filter(action=["canteen_timetable"]),
        state=[States.teacher_misc_menu_second],
    )
    async def student_canteen_timetable_handler(call: CallbackQuery):
        await States.teacher_menu.set()
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
            keyboard=TEACHER_MAIN_KEYBOARD,
            parse_mode="markdown",
        )
        await call.answer()

    # =============================
    @dp.callback_query_handler(
        cf.filter(action=["contact_devs"]),
        state=[States.teacher_misc_menu_first],
    )
    async def student_canteen_timetable_handler(call: CallbackQuery):
        await States.teacher_menu.set()
        message = call.message
        text = Texts.help_message
        await send_message(
            message,
            text=text,
            keyboard=TEACHER_MAIN_KEYBOARD,
            parse_mode="markdown",
        )
        await call.answer()

    # =============================
    @dp.callback_query_handler(
        cf.filter(action=["support_devs"]),
        state=[States.teacher_misc_menu_first],
    )
    async def student_canteen_timetable_handler(call: CallbackQuery):
        await States.teacher_menu.set()
        message = call.message
        text = Texts.donate_message
        await send_message(
            message,
            text=text,
            keyboard=TEACHER_MAIN_KEYBOARD,
            parse_mode="markdown",
        )
        await call.answer()

    # =============================
