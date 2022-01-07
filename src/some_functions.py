import asyncio
import re
from asyncio.tasks import ensure_future
from aiogram.dispatcher import FSMContext
from src.bot import bot
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.types.inline_keyboard import InlineKeyboardMarkup

from src.bot import bot, dp
from src.keyboards import (
    ADMINISTRATION_MENU_FIRST_KEYBOARD,
    CHILD_MAIN_KEYBOARD,
    STUDENT_MAIN_KEYBOARD,
    TEACHER_MAIN_KEYBOARD,
)
from src.states import States


async def send_message(
    message: Message, text: str, keyboard: InlineKeyboardMarkup, **kwargs
):
    await bot.send_message(
        chat_id=message.chat.id, text=text, reply_markup=keyboard, **kwargs
    )

    await message.edit_reply_markup(reply_markup=None)


async def dispatcher_menu(
    message: Message, role: str, text: str, parse_mode="markdown"
):
    if role == "Parent":
        await States.child_menu.set()
        await send_message(
            message, text=text, keyboard=CHILD_MAIN_KEYBOARD, parse_mode=parse_mode
        )
    elif role == "Student":
        await States.student_menu.set()
        await send_message(
            message, text=text, keyboard=STUDENT_MAIN_KEYBOARD, parse_mode=parse_mode
        )
    elif role == "Teacher":
        await States.teacher_menu.set()
        await send_message(
            message, text=text, keyboard=TEACHER_MAIN_KEYBOARD, parse_mode=parse_mode
        )
    elif role == "Administration":
        await States.administration_menu_first.set()
        await send_message(
            message,
            text=text,
            keyboard=ADMINISTRATION_MENU_FIRST_KEYBOARD,
            parse_mode=parse_mode,
        )


async def is_find_for_student(state: FSMContext):
    return (await state.get_data()).get("find_subclass_id") is not None


async def is_changing_role(state: FSMContext):
    return (await state.get_data()).get("changed")
