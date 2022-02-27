from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery
from src.api import (
    get_canteen_timetable,
    get_ring_timetable,
    get_user_day_of_week,
    get_user_today,
    get_user_tomorrow,
    get_user_week,
)
from src.bot import dp
from src.keyboards import (
    STUDENT_DAY_OF_WEEK_KEYBOARD,
    STUDENT_MAIN_KEYBOARD,
    STUDENT_MISC_MENU_FIRST_KEYBOARD,
    STUDENT_MISC_MENU_SECOND_KEYBOARD,
    cf,
)
from loguru import logger
from src.some_functions import send_message
from src.states import States
from src.texts import Texts


async def register_student_handlers():
    @dp.callback_query_handler(
        cf.filter(action=["student_menu"]),
        state=[
            States.student_day_of_week,
            States.student_misc_menu_first,
            States.student_misc_menu_second,
        ],
    )
    async def student_menu_handler(call: CallbackQuery, state: FSMContext):
        message = call.message
        if await state.get_state() == States.student_day_of_week.state:
            logger.info(
                f"{message.chat.id} | {message.chat.username} | Student | student_menu | back_day_of_week_button | None"
            )
        elif await state.get_state() == States.student_misc_menu_first.state:
            logger.info(
                f"{message.chat.id} | {message.chat.username} | Student | student_menu | back_misc_menu_first_button | None"
            )
        else:
            logger.info(
                f"{message.chat.id} | {message.chat.username} | Student | student_menu | back_misc_menu_second_button | None"
            )

        await send_message(
            message,
            text=Texts.student_main_menu,
            keyboard=STUDENT_MAIN_KEYBOARD,
            parse_mode="markdown",
        )
        await call.answer()
        await States.student_menu.set()

    # ==============================
    @dp.callback_query_handler(
        cf.filter(action=["student_day_of_week"]),
        state=[States.student_menu],
    )
    async def student_day_of_week_handler(call: CallbackQuery, state: FSMContext):
        message = call.message
        logger.info(
            f"{message.chat.id} | {message.chat.username} | Student | student_day_of_week_menu | day_of_week_menu_button | None"
        )
        await send_message(
            message,
            text=Texts.select_day_of_week,
            keyboard=STUDENT_DAY_OF_WEEK_KEYBOARD,
            parse_mode="Markdown",
        )
        await call.answer()
        await States.student_day_of_week.set()

    # ==============================
    @dp.callback_query_handler(
        cf.filter(action=["student_choose_day_of_week"]),
        state=[States.student_day_of_week],
    )
    async def student_choose_day_of_week_handler(
        call: CallbackQuery, callback_data: dict
    ):
        message = call.message
        day_of_week = int(callback_data["data"])
        logger.info(
            f"{message.chat.id} | {message.chat.username} | Student | student_day_of_week | day_of_week_button | {day_of_week}"
        )
        text = await get_user_day_of_week(
            telegram_id=message.chat.id,
            day_of_week=day_of_week,
            is_searching=False,
        )
        await send_message(
            message,
            text=text,
            keyboard=STUDENT_MAIN_KEYBOARD,
            parse_mode="MarkdownV2",
        )
        await call.answer()
        await States.student_menu.set()

    # =============================
    @dp.callback_query_handler(
        cf.filter(action=["student_misc_menu_first"]),
        state=[
            States.student_menu,
            States.student_misc_menu_second,
        ],
    )
    async def student_misc_menu_first_handler(
        call: CallbackQuery, state: FSMContext, callback_data: dict
    ):
        message = call.message
        if await state.get_state() == States.student_menu.state:
            logger.info(
                f"{message.chat.id} | {message.chat.username} | Student | student_misc_menu_first | misc_menu_button | None"
            )
        else:
            logger.info(
                f"{message.chat.id} | {message.chat.username} | Student | student_misc_menu_first | arrow_button | None"
            )
        await send_message(
            message,
            text=Texts.student_misc_menu,
            keyboard=STUDENT_MISC_MENU_FIRST_KEYBOARD,
            parse_mode="markdown",
        )
        await call.answer()
        await States.student_misc_menu_first.set()

    # =============================
    @dp.callback_query_handler(
        cf.filter(action=["student_misc_menu_second"]),
        state=[States.student_misc_menu_first],
    )
    async def student_misc_menu_second_handler(
        call: CallbackQuery, callback_data: dict
    ):
        message = call.message
        logger.info(
            f"{message.chat.id} | {message.chat.username} | Student | student_misc_menu_second | arrow_button | None"
        )
        await send_message(
            message,
            text=Texts.student_misc_menu,
            keyboard=STUDENT_MISC_MENU_SECOND_KEYBOARD,
            parse_mode="markdown",
        )
        await call.answer()
        await States.student_misc_menu_second.set()

    # =============================
    @dp.callback_query_handler(
        cf.filter(action=["today"]),
        state=[States.student_menu],
    )
    async def student_today_handler(call: CallbackQuery, callback_data: dict):
        message = call.message
        logger.info(
            f"{message.chat.id} | {message.chat.username} | Student | student_today | today_button | None"
        )
        text = await get_user_today(telegram_id=message.chat.id, is_searching=False)
        await send_message(
            message,
            text=text,
            keyboard=STUDENT_MAIN_KEYBOARD,
            parse_mode="MarkdownV2",
        )
        await call.answer()

    # =============================
    @dp.callback_query_handler(
        cf.filter(action=["tomorrow"]),
        state=[States.student_menu],
    )
    async def student_tomorrow_handler(call: CallbackQuery):
        message = call.message
        logger.info(
            f"{message.chat.id} | {message.chat.username} | Student | student_tomorrow | tomorrow_button | None"
        )
        text = await get_user_tomorrow(telegram_id=message.chat.id, is_searching=False)
        await send_message(
            message,
            text=text,
            keyboard=STUDENT_MAIN_KEYBOARD,
            parse_mode="MarkdownV2",
        )
        await call.answer()

    # =============================
    @dp.callback_query_handler(
        cf.filter(action=["week"]),
        state=[States.student_menu],
    )
    async def student_week_handler(call: CallbackQuery):
        message = call.message
        logger.info(
            f"{message.chat.id} | {message.chat.username} | Student | student_week | week_button | None"
        )
        text = await get_user_week(telegram_id=message.chat.id, is_searching=False)

        await send_message(
            message,
            text=text,
            keyboard=STUDENT_MAIN_KEYBOARD,
            parse_mode="MarkdownV2",
        )
        await call.answer()

    # =============================
    @dp.callback_query_handler(
        cf.filter(action=["ring_timetable"]),
        state=[States.student_misc_menu_first],
    )
    async def student_ring_timetable_handler(call: CallbackQuery):
        message = call.message
        logger.info(
            f"{message.chat.id} | {message.chat.username} | Student | student_ring_timetable | ring_timetable_button | None"
        )
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
            keyboard=STUDENT_MAIN_KEYBOARD,
            parse_mode="markdown",
        )
        await call.answer()
        await States.student_menu.set()

    # =============================
    @dp.callback_query_handler(
        cf.filter(action=["canteen_timetable"]),
        state=[States.student_misc_menu_second],
    )
    async def student_canteen_timetable_handler(call: CallbackQuery):
        message = call.message
        logger.info(
            f"{message.chat.id} | {message.chat.username} | Student | student_canteen_timetable | canteen_timetable_button | None"
        )

        text = await get_canteen_timetable(message.chat.id)

        await send_message(
            message,
            text=text,
            keyboard=STUDENT_MAIN_KEYBOARD,
            parse_mode="MarkdownV2",
        )
        await call.answer()
        await States.student_menu.set()

    # =============================
    @dp.callback_query_handler(
        cf.filter(action=["contact_devs"]),
        state=[States.student_misc_menu_first],
    )
    async def student_contact_devs_handler(call: CallbackQuery):
        message = call.message
        logger.info(
            f"{message.chat.id} | {message.chat.username} | Student | student_contact_devs | contact_devs_button | None"
        )
        text = Texts.help_message.format(telegram_id=message.chat.id)
        await send_message(
            message,
            text=text,
            keyboard=STUDENT_MAIN_KEYBOARD,
            parse_mode="markdown",
        )
        await call.answer()
        await States.student_menu.set()

    # =============================
    @dp.callback_query_handler(
        cf.filter(action=["support_devs"]),
        state=[States.student_misc_menu_first],
    )
    async def student_support_devs_handler(call: CallbackQuery):
        message = call.message
        logger.info(
            f"{message.chat.id} | {message.chat.username} | Student | student_support_devs | support_devs_button | None"
        )
        text = Texts.donate_message
        await send_message(
            message,
            text=text,
            keyboard=STUDENT_MAIN_KEYBOARD,
            parse_mode="markdown",
        )
        await call.answer()
        await States.student_menu.set()

    # =============================

    @dp.callback_query_handler(
        cf.filter(action=["anouns"]),
        state=[States.student_misc_menu_second],
    )
    async def student_announcements_handler(call: CallbackQuery):
        message = call.message
        logger.info(
            f"{message.chat.id} | {message.chat.username} | Student | student_announcements | announcements_button | None"
        )
        text = Texts.announcements
        await send_message(
            message,
            text=text,
            keyboard=STUDENT_MAIN_KEYBOARD,
            parse_mode="markdown",
        )
        await call.answer()
        await States.student_menu.set()

    # =============================
