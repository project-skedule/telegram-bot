from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, Message

from src.api import (
    get_canteen_timetable,
    get_ring_timetable,
    get_user_day_of_week,
    get_user_today,
    get_user_tomorrow,
    get_user_week,
)
from src.bot import bot, dp
from src.keyboards import (
    CHILD_DAY_OF_WEEK_KEYBOARD,
    CHILD_MAIN_KEYBOARD,
    CHILD_MISC_MENU_FIRST_KEYBOARD,
    PARENT_MISC_MENU_FIRST_KEYBOARD,
    cf,
    get_child_keyboard,
)
from src.logger import logger
from src.some_functions import send_message
from src.states import States
from src.texts.texts import Texts


async def register_parent_handlers():
    @dp.callback_query_handler(
        cf.filter(action=["choose_child"]),
        state=[
            States.add_more_childs,
            States.child_menu,
            States.find_menu,
            States.find_day_of_week,
            States.parent_misc_menu_first,
            States.show_childs,
        ],
    )
    async def choose_child_handler(call: CallbackQuery):
        await States.choose_child.set()
        message = call.message
        await send_message(
            message,
            Texts.choose_children,
            await get_child_keyboard(message.chat.id),
            parse_mode="markdown",
        )
        await call.answer()

    # ==============================
    @dp.callback_query_handler(
        cf.filter(action=["child_menu"]),
        state=[
            States.choose_child,
            States.child_day_of_week,
            States.child_misc_menu_first,
        ],
    )
    async def child_menu_handler(
        call: CallbackQuery, callback_data: dict, state: FSMContext
    ):
        await States.child_menu.set()
        message = call.message
        if callback_data["data"] != "0":
            await state.update_data({"child": callback_data["data"]})

        # FIX: what is going on here?
        await send_message(
            message,
            f"child menu {(await state.get_data())['child']}",
            CHILD_MAIN_KEYBOARD,
        )
        await call.answer()

    # ==============================
    @dp.callback_query_handler(
        cf.filter(action=["child_day_of_week"]),
        state=[States.child_menu],
    )
    async def child_day_of_week_handler(call: CallbackQuery):
        await States.child_day_of_week.set()
        message = call.message
        await send_message(
            message,
            text=Texts.select_day_of_week,
            keyboard=CHILD_DAY_OF_WEEK_KEYBOARD,
            parse_mode="markdown",
        )

        await call.answer()

    # ==============================
    @dp.callback_query_handler(
        cf.filter(action=["child_choose_day_of_week"]),
        state=[States.child_day_of_week],
    )
    async def child_choose_day_of_week_handler(
        call: CallbackQuery, callback_data: dict, state: FSMContext
    ):
        await States.child_menu.set()
        message = call.message
        # FIX format
        text = await get_user_day_of_week(
            telegram_id=(await state.get_data())["child"],
            day_of_week=callback_data["data"],
            is_searching=False,
        )
        await send_message(
            message, text=text, keyboard=CHILD_MAIN_KEYBOARD, parse_mode="markdown"
        )
        await call.answer()

    # =============================
    @dp.callback_query_handler(
        cf.filter(action=["child_misc_menu_first"]),
        state=[States.child_menu],
    )
    async def child_misc_menu_first_handler(call: CallbackQuery, callback_data: dict):
        await States.child_misc_menu_first.set()
        message = call.message
        await send_message(
            message,
            text=Texts.student_main_menu,  # NOTE: should we use student menu or create child menu?
            keyboard=CHILD_MISC_MENU_FIRST_KEYBOARD,
            parse_mode="markdown",
        )
        await call.answer()

    # =============================
    @dp.callback_query_handler(
        cf.filter(action=["parent_misc_menu_first"]),
        state=[States.choose_child],
    )
    async def parent_misc_menu_first_handler(call: CallbackQuery, callback_data: dict):
        await States.parent_misc_menu_first.set()
        message = call.message
        await send_message(
            message,
            text=Texts.parent_main_menu,
            keyboard=PARENT_MISC_MENU_FIRST_KEYBOARD,
            parse_mode="markdown",
        )
        await call.answer()

    # =============================
    @dp.callback_query_handler(
        cf.filter(action=["today"]),
        state=[States.child_menu],
    )
    async def student_today_handler(call: CallbackQuery, state: FSMContext):
        await States.child_menu.set()
        message = call.message
        # FIX: format
        text = await get_user_today(
            telegram_id=(await state.get_data())["child"], is_searching=False
        )
        await send_message(
            message, text=text, keyboard=CHILD_MAIN_KEYBOARD, parse_mode="markdown"
        )
        await call.answer()

    # =============================
    @dp.callback_query_handler(
        cf.filter(action=["tomorrow"]),
        state=[States.child_menu],
    )
    async def student_tomorrow_handler(call: CallbackQuery, state: FSMContext):
        await States.child_menu.set()
        message = call.message
        # FIX format
        text = await get_user_tomorrow(
            telegram_id=(await state.get_data())["child"], is_searching=False
        )
        await send_message(
            message, text=text, keyboard=CHILD_MAIN_KEYBOARD, parse_mode="markdown"
        )
        await call.answer()

    # =============================
    @dp.callback_query_handler(
        cf.filter(action=["week"]),
        state=[States.child_menu],
    )
    async def student_week_handler(call: CallbackQuery, state: FSMContext):
        await States.child_menu.set()
        message = call.message
        # FIX: format
        text = await get_user_week(
            telegram_id=(await state.get_data())["child"], is_searching=False
        )
        await send_message(
            message, text=text, keyboard=CHILD_MAIN_KEYBOARD, parse_mode="markdown"
        )
        await call.answer()

    # =============================
    @dp.callback_query_handler(
        cf.filter(action=["ring_timetable"]),
        state=[States.child_misc_menu_first],
    )
    async def student_ring_timetable_handler(call: CallbackQuery, state: FSMContext):
        await States.child_menu.set()
        message = call.message
        data = await get_ring_timetable(message.chat.id)
        # FIX: add break
        text = Texts.rings_timetable_header + "".join(
            Texts.rings_timetable_format.format(
                lesson_number=lsn["number"],
                time=lsn["time_start"] + " - " + lsn["time_end"],
            )
            for lsn in data
        )
        await send_message(
            message, text=text, keyboard=CHILD_MAIN_KEYBOARD, parse_mode="markdown"
        )
        await call.answer()

    # =============================
    @dp.callback_query_handler(
        cf.filter(action=["canteen_timetable"]),
        state=[States.child_misc_menu_first],
    )
    async def student_canteen_timetable_handler(call: CallbackQuery, state: FSMContext):
        await States.child_menu.set()
        message = call.message
        canteens = await get_canteen_timetable(message.chat.id)
        text = Texts.canteen_timetable_header + "".join(
            Texts.canteen_timetable_format.format(
                corpus_name=corpus_name, canteen_text=canteen_text
            )
            for corpus_name, canteen_text in canteens.items()
        )
        await send_message(
            message, text=text, keyboard=CHILD_MAIN_KEYBOARD, parse_mode="markdown"
        )
        await call.answer()
