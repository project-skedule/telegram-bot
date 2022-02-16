from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery
from src.bot import dp
from src.keyboards import (
    ADMINISTRATION_MENU_FIRST_KEYBOARD,
    CHILD_MAIN_KEYBOARD,
    STUDENT_MAIN_KEYBOARD,
    TEACHER_MAIN_KEYBOARD,
    cf,
)
from src.logger import logger
from src.some_functions import send_message
from src.states import States
from src.texts import Texts


async def register_universal_handlers():
    @dp.callback_query_handler(cf.filter(action=["main_menu"]), state="*")
    async def menu_handler(call: CallbackQuery, state: FSMContext):
        message = call.message
        role = (await state.get_data())["role"]

        if role == "Parent":
            await send_message(
                message,
                text=Texts.parent_main_menu,
                keyboard=CHILD_MAIN_KEYBOARD,
                parse_mode="markdown",
            )
            await States.child_menu.set()
        elif role == "Student":
            await send_message(
                message,
                text=Texts.student_main_menu,
                keyboard=STUDENT_MAIN_KEYBOARD,
                parse_mode="markdown",
            )
            await States.student_menu.set()
        elif role == "Teacher":
            await send_message(
                message,
                text=Texts.teacher_main_menu,
                keyboard=TEACHER_MAIN_KEYBOARD,
                parse_mode="markdown",
            )
            await States.teacher_menu.set()
        elif role == "Administration":
            await send_message(
                message,
                text=Texts.admin_main_menu,
                keyboard=ADMINISTRATION_MENU_FIRST_KEYBOARD,
                parse_mode="markdown",
            )
            await States.administration_menu_first.set()

        await call.answer()
