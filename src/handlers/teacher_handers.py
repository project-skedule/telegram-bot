from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, Message
from ..text_loader import Texts
from ..api import (
    get_canteen_timetable,
    get_ring_timetable,
    get_teacher_day_of_week,
    get_teacher_next_lesson,
    get_teacher_today,
    get_teacher_tomorrow,
    get_teacher_week,
)
from ..bot import bot, dp
from ..keyboards import (
    TEACHER_DAY_OF_WEEK_KEYBOARD,
    TEACHER_MAIN_KEYBOARD,
    TEACHER_MISC_MENU_FIRST_KEYBOARD,
    TEACHER_MISC_MENU_SECOND_KEYBOARD,
    cf,
)
from ..logger import logger
from ..some_functions import send_message
from ..states import States


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
            text="teacher menu",
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
        text = await get_teacher_day_of_week(
            user_id=message.chat.id, day=callback_data["data"]
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
            text="teacher misc menu #1",
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
            text="teacher misc menu #2",
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
        text = await get_teacher_next_lesson(user_id=message.chat.id)
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
        text = await get_teacher_today(user_id=message.chat.id)
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
        text = await get_teacher_tomorrow(user_id=message.chat.id)
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
        text = await get_teacher_week(user_id=message.chat.id)
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
        text = await get_ring_timetable(message.chat.id)
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
        text = await get_canteen_timetable(message.chat.id)
        await send_message(
            message,
            text=text,
            keyboard=TEACHER_MAIN_KEYBOARD,
            parse_mode="markdown",
        )
        await call.answer()
