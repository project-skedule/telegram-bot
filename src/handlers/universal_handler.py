from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery
from src.bot import dp
from src.keyboards import (
    ADMINISTRATION_MENU_FIRST_KEYBOARD,
    CHILD_MAIN_KEYBOARD,
    FREE_CABINET_ARROW_KEYBOARD,
    STUDENT_MAIN_KEYBOARD,
    TEACHER_MAIN_KEYBOARD,
    cf,
)
from loguru import logger
from src.some_functions import send_message
from src.states import States
from src.texts import Texts
from src.config import COUNT_CABINETS_PER_PAGE


async def register_universal_handlers():
    @dp.callback_query_handler(cf.filter(action=["main_menu"]), state="*")
    async def menu_handler(call: CallbackQuery, state: FSMContext):
        message = call.message
        role = (await state.get_data())["role"]

        if role == "Parent":
            logger.info(
                f"{message.chat.id} | {message.chat.username} | {role} | parent_show_childs | main_menu_callback | None"
            )
            await send_message(
                message,
                text=Texts.parent_main_menu,
                keyboard=CHILD_MAIN_KEYBOARD,
                parse_mode="markdown",
            )
            await States.child_menu.set()
        elif role == "Student":
            logger.info(
                f"{message.chat.id} | {message.chat.username} | {role} | student_menu | main_menu_callback | None"
            )
            await send_message(
                message,
                text=Texts.student_main_menu,
                keyboard=STUDENT_MAIN_KEYBOARD,
                parse_mode="markdown",
            )
            await States.student_menu.set()
        elif role == "Teacher":
            logger.info(
                f"{message.chat.id} | {message.chat.username} | {role} | teacher_menu | main_menu_callback | None"
            )
            await send_message(
                message,
                text=Texts.teacher_main_menu,
                keyboard=TEACHER_MAIN_KEYBOARD,
                parse_mode="markdown",
            )
            await States.teacher_menu.set()
        elif role == "Administration":
            logger.info(
                f"{message.chat.id} | {message.chat.username} | {role} | administration_menu_first | main_menu_callback | None"
            )
            await send_message(
                message,
                text=Texts.admin_main_menu,
                keyboard=ADMINISTRATION_MENU_FIRST_KEYBOARD,
                parse_mode="markdown",
            )
            await States.administration_menu_first.set()

        await call.answer()

    # =================================================================

    @dp.callback_query_handler(
        cf.filter(action=["left"]),
        state=[States.show_free_cabinets],
    )
    async def free_cabinets_left_arrow_handler(
        call: CallbackQuery, state: FSMContext, callback_data: dict
    ):
        message = call.message
        role = (await state.get_data())["role"]
        logger.info(
            f"{message.chat.id} | {message.chat.username} | {role} | show_free_cabinets | arrow_button | left"
        )
        cabinets = (await state.get_data())["cabinets"]
        cabinets["page"] = cabinets["page"] - 1
        if cabinets["page"] == -1:
            cabinets["page"] = len(cabinets["cabinets"]) // COUNT_CABINETS_PER_PAGE
        await state.update_data({"cabinets": cabinets})
        text_cabinets = ""
        for cabinet in cabinets["cabinets"][
            cabinets["page"]
            * COUNT_CABINETS_PER_PAGE : COUNT_CABINETS_PER_PAGE
            * (cabinets["page"] + 1)
        ]:
            text_cabinets += cabinet["name"] + "\n"
        await send_message(
            message,
            text=Texts.free_cabinets.format(
                lesson_number=cabinets["lesson_number"],
                corpus_name=cabinets["corpus_name"],
            )
            + text_cabinets,
            keyboard=FREE_CABINET_ARROW_KEYBOARD,
            parse_mode="markdown",
        )
        await call.answer()

    # =============================

    @dp.callback_query_handler(
        cf.filter(action=["right"]),
        state=[States.show_free_cabinets],
    )
    async def free_cabinets_left_arrow_handler(
        call: CallbackQuery, state: FSMContext, callback_data: dict
    ):
        message = call.message
        role = (await state.get_data())["role"]
        logger.info(
            f"{message.chat.id} | {message.chat.username} | {role} | show_free_cabinets | arrow_button | right"
        )
        cabinets = (await state.get_data())["cabinets"]
        cabinets["page"] = cabinets["page"] + 1
        if cabinets["page"] > len(cabinets["cabinets"]) // COUNT_CABINETS_PER_PAGE:
            cabinets["page"] = 0
        await state.update_data({"cabinets": cabinets})
        text_cabinets = ""
        for cabinet in cabinets["cabinets"][
            cabinets["page"]
            * COUNT_CABINETS_PER_PAGE : COUNT_CABINETS_PER_PAGE
            * (cabinets["page"] + 1)
        ]:
            text_cabinets += cabinet["name"] + "\n"
        await send_message(
            message,
            text=Texts.free_cabinets.format(
                lesson_number=cabinets["lesson_number"],
                corpus_name=cabinets["corpus_name"],
            )
            + text_cabinets,
            keyboard=FREE_CABINET_ARROW_KEYBOARD,
            parse_mode="markdown",
        )
        await call.answer()
