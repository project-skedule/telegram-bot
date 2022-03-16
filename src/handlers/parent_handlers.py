import ujson
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, Message
from src.api import (
    delete_child,
    get_canteen_timetable,
    get_ring_timetable,
    get_user_day_of_week,
    get_user_today,
    get_user_tomorrow,
    get_user_week,
)
from src.bot import dp
from src.keyboards import (
    CHILD_DAY_OF_WEEK_KEYBOARD,
    CHILD_MAIN_KEYBOARD,
    CHILD_MISC_MENU_FIRST_KEYBOARD,
    PARENT_MISC_MENU_FIRST_KEYBOARD,
    SUBMIT_DELETE_CHILD_KEYBOARD,
    cf,
    get_child_keyboard,
    get_childs_to_delete_keyboard,
)
from loguru import logger
from src.redis import get_child_by_id
from src.some_functions import send_message
from src.states import States
from src.texts import Texts


async def register_parent_handlers():
    @dp.callback_query_handler(
        cf.filter(action=["show_childs"]),
        state=[
            States.child_menu,
            States.parent_misc_menu_first,
            States.choose_delete_child,
            States.submit_delete_child,
        ],
    )
    async def show_childs_handler(
        call: CallbackQuery, state: FSMContext, callback_data: dict
    ):
        message = call.message

        last_state = await state.get_state()
        if last_state == States.child_menu.state:
            logger.info(
                f"{message.chat.id} | {message.chat.username} | Parent | parent_show_childs | back_child_button | None"
            )
        elif last_state == States.parent_misc_menu_first.state:
            logger.info(
                f"{message.chat.id} | {message.chat.username} | Parent | parent_show_childs | back_parent_misc_menu_button | None"
            )
        elif last_state == States.choose_delete_child.state:
            logger.info(
                f"{message.chat.id} | {message.chat.username} | Parent | parent_show_childs | back_delete_child_button | None"
            )
        else:
            logger.info(
                f"{message.chat.id} | {message.chat.username} | Parent | parent_show_childs | submit_delete_child_button_yes | None"
            )

        if callback_data["data"] == "delete_child":
            child_id = (await state.get_data())["delete_child_id"]
            child_name = (await state.get_data())["delete_child_name"]
            await delete_child(message.chat.id, child_id)
            await send_message(
                message,
                Texts.successful_delete_child.format(child_name=child_name),
                await get_child_keyboard(message.chat.id),
                parse_mode="markdown",
            )

        else:
            await send_message(
                message,
                Texts.choose_children,
                await get_child_keyboard(message.chat.id),
                parse_mode="markdown",
            )
        await call.answer()
        await States.show_childs.set()

    # ==============================
    @dp.callback_query_handler(
        cf.filter(action=["child_menu"]),
        state=[
            States.show_childs,
            States.child_day_of_week,
            States.child_misc_menu_first,
        ],
    )
    async def child_menu_handler(
        call: CallbackQuery, state: FSMContext, callback_data: dict
    ):
        message = call.message
        last_state = await state.get_state()
        if last_state == States.show_childs.state:
            child_id = int(callback_data["data"])
            child = await get_child_by_id(message.chat.id, child_id)
            await state.update_data({"current_child_id": child["subclass_id"]})  # FIXME
            await state.update_data({"current_child_name": child["name"]})
            await state.update_data({"current_child_school_id": child["school_id"]})
            logger.info(
                f"{message.chat.id} | {message.chat.username} | Parent | child_menu | child_button | child['name']"
            )

        elif last_state == States.child_day_of_week.state:
            logger.info(
                f"{message.chat.id} | {message.chat.username} | Parent | child_menu | back_day_of_week_menu_button | None"
            )
        else:
            logger.info(
                f"{message.chat.id} | {message.chat.username} | Parent | child_menu | back_misc_menu_first_button | None"
            )

        await send_message(
            message,
            Texts.child_menu.format(
                child_name=(await state.get_data())["current_child_name"]
            ),
            CHILD_MAIN_KEYBOARD,
        )
        await call.answer()
        await States.child_menu.set()

    # ==============================
    @dp.callback_query_handler(
        cf.filter(action=["child_day_of_week"]),
        state=[States.child_menu],
    )
    async def child_day_of_week_handler(call: CallbackQuery):
        message = call.message
        logger.info(
            f"{message.chat.id} | {message.chat.username} | Parent | child_day_of_week_menu | day_of_week_menu_button | None"
        )
        await send_message(
            message,
            text=Texts.select_day_of_week,
            keyboard=CHILD_DAY_OF_WEEK_KEYBOARD,
            parse_mode="markdown",
        )

        await call.answer()
        await States.child_day_of_week.set()

    # ==============================
    @dp.callback_query_handler(
        cf.filter(action=["child_choose_day_of_week"]),
        state=[States.child_day_of_week],
    )
    async def child_choose_day_of_week_handler(
        call: CallbackQuery, callback_data: dict, state: FSMContext
    ):
        message = call.message
        day_of_week = int(callback_data["data"])
        logger.info(
            f"{message.chat.id} | {message.chat.username} | Parent | child_day_of_week | day_of_week_button | {day_of_week}"
        )
        text = await get_user_day_of_week(
            telegram_id=message.chat.id,
            is_searching=True,
            subclass_id=(await state.get_data())["current_child_id"],
            child_name=(await state.get_data())["current_child_name"],
            day_of_week=day_of_week,
        )
        await send_message(
            message,
            text=text,
            keyboard=CHILD_MAIN_KEYBOARD,
            parse_mode="MarkdownV2",
        )
        await call.answer()
        await States.child_menu.set()

    # =============================
    @dp.callback_query_handler(
        cf.filter(action=["child_misc_menu_first"]),
        state=[States.child_menu],
    )
    async def child_misc_menu_first_handler(call: CallbackQuery, callback_data: dict):
        message = call.message
        logger.info(
            f"{message.chat.id} | {message.chat.username} | Parent | child_misc_menu_first | misc_menu_button | None"
        )
        await send_message(
            message,
            text=Texts.student_main_menu,  # NOTE: should we use student menu or create child menu?
            keyboard=CHILD_MISC_MENU_FIRST_KEYBOARD,
            parse_mode="markdown",
        )
        await call.answer()
        await States.child_misc_menu_first.set()

    # =============================
    @dp.callback_query_handler(
        cf.filter(action=["parent_misc_menu_first"]),
        state=[States.show_childs],
    )
    async def parent_misc_menu_first_handler(call: CallbackQuery, callback_data: dict):
        message = call.message
        logger.info(
            f"{message.chat.id} | {message.chat.username} | Parent | parent_misc_menu_first | misc_menu_button | None"
        )
        await send_message(
            message,
            text=Texts.parent_misc_menu,
            keyboard=PARENT_MISC_MENU_FIRST_KEYBOARD,
            parse_mode="markdown",
        )
        await call.answer()
        await States.parent_misc_menu_first.set()

    # =============================
    @dp.callback_query_handler(
        cf.filter(action=["today"]),
        state=[States.child_menu],
    )
    async def child_today_handler(call: CallbackQuery, state: FSMContext):
        message = call.message
        logger.info(
            f"{message.chat.id} | {message.chat.username} | Parent | child_today | today_button | None"
        )
        text = await get_user_today(
            telegram_id=message.chat.id,
            is_searching=True,
            subclass_id=(await state.get_data())["current_child_id"],
            child_name=(await state.get_data())["current_child_name"],
        )
        await send_message(
            message, text=text, keyboard=CHILD_MAIN_KEYBOARD, parse_mode="MarkdownV2"
        )
        await call.answer()
        await States.child_menu.set()

    # =============================
    @dp.callback_query_handler(
        cf.filter(action=["tomorrow"]),
        state=[States.child_menu],
    )
    async def child_tomorrow_handler(call: CallbackQuery, state: FSMContext):
        message = call.message
        logger.info(
            f"{message.chat.id} | {message.chat.username} | Parent | child_tomorrow | tomorrow_button | None"
        )
        text = await get_user_tomorrow(
            telegram_id=message.chat.id,
            is_searching=True,
            subclass_id=(await state.get_data())["current_child_id"],
            child_name=(await state.get_data())["current_child_name"],
        )
        await send_message(
            message,
            text=text,
            keyboard=CHILD_MAIN_KEYBOARD,
            parse_mode="MarkdownV2",
        )
        await call.answer()
        await States.child_menu.set()

    # =============================
    @dp.callback_query_handler(
        cf.filter(action=["week"]),
        state=[States.child_menu],
    )
    async def child_week_handler(call: CallbackQuery, state: FSMContext):
        message = call.message
        logger.info(
            f"{message.chat.id} | {message.chat.username} | Parent | child_week | week_button | None"
        )
        text = await get_user_week(
            telegram_id=message.chat.id,
            is_searching=True,
            subclass_id=(await state.get_data())["current_child_id"],
            child_name=(await state.get_data())["current_child_name"],
        )
        await send_message(
            message,
            text=text,
            keyboard=CHILD_MAIN_KEYBOARD,
            parse_mode="MarkdownV2",
        )
        await call.answer()
        await States.child_menu.set()

    # =============================
    @dp.callback_query_handler(
        cf.filter(action=["ring_timetable"]),
        state=[States.child_misc_menu_first],
    )
    async def child_ring_timetable_handler(call: CallbackQuery, state: FSMContext):
        message = call.message
        logger.info(
            f"{message.chat.id} | {message.chat.username} | Parent | child_ring_timetable | ring_timetable_button | None"
        )
        data = await get_ring_timetable(
            school_id=(await state.get_data())["current_child_school_id"]
        )
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
        await States.child_menu.set()

    # =============================
    @dp.callback_query_handler(
        cf.filter(action=["canteen_timetable"]),
        state=[States.child_misc_menu_first],
    )
    async def child_canteen_timetable_handler(call: CallbackQuery, state: FSMContext):
        message = call.message
        logger.info(
            f"{message.chat.id} | {message.chat.username} | Parent | child_canteen_timetable | canteen_timetable_button | None"
        )
        text = await get_canteen_timetable(
            school_id=(await state.get_data())["current_child_school_id"]
        )
        await send_message(
            message,
            text=text,
            keyboard=CHILD_MAIN_KEYBOARD,
            parse_mode="MarkdownV2",
        )
        await call.answer()
        await States.child_menu.set()

    # =============================
    @dp.callback_query_handler(
        cf.filter(action=["delete_child"]),
        state=[States.show_childs],
    )
    async def delete_child_handler(call: CallbackQuery, state: FSMContext):
        message = call.message
        logger.info(
            f"{message.chat.id} | {message.chat.username} | Parent | delete_child_menu | delete_child_button | None"
        )

        await send_message(
            message,
            text=Texts.choose_delete_child,
            keyboard=await get_childs_to_delete_keyboard(message.chat.id),
            parse_mode="markdown",
        )
        await call.answer()
        await States.choose_delete_child.set()

    # =============================
    @dp.callback_query_handler(
        cf.filter(action=["submit_delete_child"]),
        state=[States.choose_delete_child],
    )
    async def submit_delete_child_handler(
        call: CallbackQuery, state: FSMContext, callback_data: dict
    ):
        message = call.message

        child_id = int(callback_data["data"])
        child_name = (await get_child_by_id(message.chat.id, child_id))["name"]
        logger.info(
            f"{message.chat.id} | {message.chat.username} | Parent | submit_delete_child_menu | submit_delete_child_button | {child_name}"
        )

        await state.update_data({"delete_child_name": child_name})
        await state.update_data({"delete_child_id": child_id})
        await send_message(
            message,
            text=Texts.submit_delete_child.format(child_name=child_name),
            keyboard=SUBMIT_DELETE_CHILD_KEYBOARD,
            parse_mode="markdown",
        )
        await call.answer()
        await States.submit_delete_child.set()

    # =============================
    @dp.callback_query_handler(
        cf.filter(action=["support_devs"]),
        state=[States.parent_misc_menu_first],
    )
    async def support_devs_parent_handler(
        call: CallbackQuery, state: FSMContext, callback_data: dict
    ):
        message = call.message
        logger.info(
            f"{message.chat.id} | {message.chat.username} | Parent | parent_support_devs | support_devs_button | None"
        )
        await send_message(
            message,
            text=Texts.donate_message,
            keyboard=PARENT_MISC_MENU_FIRST_KEYBOARD,
            parse_mode="markdown",
        )
        await call.answer()

    # =============================
    @dp.callback_query_handler(
        cf.filter(action=["contact_devs"]),
        state=[States.parent_misc_menu_first],
    )
    async def contact_devs_parent_handler(
        call: CallbackQuery, state: FSMContext, callback_data: dict
    ):
        message = call.message
        logger.info(
            f"{message.chat.id} | {message.chat.username} | Parent | parent_contact_devs | contact_devs_button | None"
        )
        await send_message(
            message,
            text=Texts.help_message.format(telegram_id=message.chat.id),
            keyboard=PARENT_MISC_MENU_FIRST_KEYBOARD,
            parse_mode="markdown",
        )
        await call.answer()
