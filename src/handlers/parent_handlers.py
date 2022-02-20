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
from src.logger import logger
from src.some_functions import send_message
from src.states import States
from src.texts import Texts


async def register_parent_handlers():
    @dp.callback_query_handler(
        cf.filter(action=["show_childs"]),
        state=[
            States.child_menu,
            States.parent_misc_menu_first,
            States.child_misc_menu_first,
            States.choose_delete_child,
            States.submit_delete_child,
        ],
    )
    async def show_childs_handler(
        call: CallbackQuery, state: FSMContext, callback_data: dict
    ):
        message = call.message
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
        logger.debug(f"{callback_data}")
        if callback_data["data"] != "0":
            data = ujson.loads(callback_data["data"].replace("'", '"'))

            await state.update_data({"current_child_id": data[0]})
            await state.update_data({"current_child_name": data[1]})
            await state.update_data({"current_child_school_id": data[2]})

        message = call.message
        # if callback_data["data"] != "0":
        #     await state.update_data({"child": callback_data["data"]})

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
        await States.child_menu.set()
        message = call.message
        text = await get_user_day_of_week(
            telegram_id=message.chat.id,
            is_searching=True,
            subclass_id=(await state.get_data())["current_child_id"],
            child_name=(await state.get_data())["current_child_name"],
            day_of_week=int(callback_data["data"]),
        )
        await send_message(
            message,
            text=text,
            keyboard=CHILD_MAIN_KEYBOARD,
            parse_mode="MarkdownV2",
        )
        await call.answer()

    # =============================
    @dp.callback_query_handler(
        cf.filter(action=["child_misc_menu_first"]),
        state=[States.child_menu],
    )
    async def child_misc_menu_first_handler(call: CallbackQuery, callback_data: dict):
        message = call.message
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
        await send_message(
            message,
            text=Texts.parent_main_menu,
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
    async def student_today_handler(call: CallbackQuery, state: FSMContext):
        message = call.message
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
    async def student_tomorrow_handler(call: CallbackQuery, state: FSMContext):
        message = call.message
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
    async def student_week_handler(call: CallbackQuery, state: FSMContext):
        await States.child_menu.set()
        message = call.message
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

    # =============================
    @dp.callback_query_handler(
        cf.filter(action=["ring_timetable"]),
        state=[States.child_misc_menu_first],
    )
    async def child_ring_timetable_handler(call: CallbackQuery, state: FSMContext):
        message = call.message
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
        canteens = await get_canteen_timetable(
            school_id=(await state.get_data())["current_child_school_id"]
        )
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
        await States.child_menu.set()

    # =============================
    @dp.callback_query_handler(
        cf.filter(action=["delete_child"]),
        state=[States.show_childs],
    )
    async def delete_child_handler(call: CallbackQuery, state: FSMContext):
        logger.debug("delete child")
        message = call.message

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
        logger.debug(f"submit delete child callback: {callback_data}")

        message = call.message
        data = ujson.loads(callback_data["data"].replace("'", '"'))
        child_name, child_id = data
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
