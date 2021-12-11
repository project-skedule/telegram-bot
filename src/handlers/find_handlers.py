from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, Message
from src.texts import Texts

from src.api import (
    get_subclass_by_params,
    get_user_day_of_week,
    get_user_next_lesson,
    get_user_today,
    get_user_tomorrow,
    get_user_week,
)

from src.bot import bot, dp
from src.keyboards import (
    FIND_DAY_OF_WEEK_KEYBOARD,
    FIND_MAIN_KEYBOARD,
    FIND_STUDENT_SUBMIT_KEYBOARD,
    FIND_TEACHER_SUBMIT_KEYBOARD,
    cf,
    find_get_teachers_keyboard,
    get_find_enter_group_keyboard,
    get_find_enter_letter_keyboard,
    get_find_enter_parallel_keyboard,
)
from src.logger import logger
from src.some_functions import dispatcher_menu, is_find_for_student, send_message
from src.states import States
from src.redis import get_school_id


async def register_find_handlers():
    @dp.callback_query_handler(
        cf.filter(action=["find_class"]),
        state=[
            States.child_misc_menu_first,
            States.student_misc_menu_first,
            States.teacher_misc_menu_first,
            States.administration_menu_first,
            States.find_student_submit,
        ],
    )
    async def find_class_handler(call: CallbackQuery, state: FSMContext):
        await States.find_enter_parallel.set()
        await state.update_data({"find_subclass_id": None})
        await state.update_data({"find_teacher_id": None})

        message = call.message
        await send_message(
            message,
            Texts.enter_parallel,
            await get_find_enter_parallel_keyboard(message.chat.id),
        )
        await call.answer()

    # =============================
    @dp.callback_query_handler(
        cf.filter(action=["find_enter_letter"]),
        state=[States.find_enter_parallel],
    )
    async def find_enter_letter_handler(
        call: CallbackQuery, state: FSMContext, callback_data: dict
    ):
        await States.find_enter_letter.set()
        parallel = callback_data["data"]
        await state.update_data({"find_parallel": f"{parallel}"})
        message = call.message
        await send_message(
            message,
            Texts.enter_letter,
            await get_find_enter_letter_keyboard(message.chat.id, parallel),
        )
        await call.answer()

    # =============================
    @dp.callback_query_handler(
        cf.filter(action=["find_enter_group"]),
        state=[States.find_enter_letter],
    )
    async def find_enter_group_handler(
        call: CallbackQuery, state: FSMContext, callback_data: dict
    ):
        await States.find_enter_group.set()
        parallel = (await state.get_data())["find_parallel"]
        letter = callback_data["data"]
        await state.update_data({"find_letter": letter})
        message = call.message
        await send_message(
            message,
            Texts.enter_group,
            await get_find_enter_group_keyboard(message.chat.id, parallel, letter),
        )
        await call.answer()

    # =============================
    @dp.callback_query_handler(
        cf.filter(action=["find_student_submit"]),
        state=[States.find_enter_group],
    )
    async def find_student_submit_handler(
        call: CallbackQuery, state: FSMContext, callback_data: dict
    ):
        message = call.message
        await States.find_student_submit.set()
        await state.update_data({"find_group": callback_data["data"]})
        parallel = (await state.get_data())["find_parallel"]
        letter = (await state.get_data())["find_letter"]
        group = (await state.get_data())["find_group"]
        subclass_id = await get_subclass_by_params(
            await get_school_id(message.chat.id), parallel, letter, group
        )
        await state.update_data({"find_subclass_id": subclass_id})
        message = call.message
        await send_message(
            message,
            Texts.confirm_class.format(subclass=f"{parallel}{letter}{group}"),
            FIND_STUDENT_SUBMIT_KEYBOARD,
        )

        await call.answer()

    # =============================
    @dp.callback_query_handler(
        cf.filter(action=["find_menu"]),
        state=[
            States.find_student_submit,
            States.find_teacher_submit,
            States.find_day_of_week,
        ],
    )
    async def find_menu_handler(
        call: CallbackQuery, state: FSMContext, callback_data: dict
    ):
        await States.find_menu.set()
        message = call.message

        if await is_find_for_student(state):
            text = f"Расписание ученика `{(await state.get_data())['find_subclass_id']}` класса"
        else:
            text = f"Расписание учителя `{(await state.get_data())['find_teacher_id']}`"
        await send_message(
            message,
            text=text,
            keyboard=FIND_MAIN_KEYBOARD,
            parse_mode="markdown",
        )
        await call.answer()

    # =============================
    @dp.callback_query_handler(
        cf.filter(action=["find_day_of_week"]),
        state=[States.find_menu],
    )
    async def find_day_of_week_handler(
        call: CallbackQuery, state: FSMContext, callback_data: dict
    ):
        await States.find_day_of_week.set()
        message = call.message

        await send_message(
            message,
            text=Texts.select_day_of_week,
            keyboard=FIND_DAY_OF_WEEK_KEYBOARD,
            parse_mode="markdown",
        )
        await call.answer()

    # =============================
    @dp.callback_query_handler(
        cf.filter(action=["find_choose_day_of_week"]),
        state=[States.find_day_of_week],
    )
    async def find_choose_day_of_week_handler(
        call: CallbackQuery, state: FSMContext, callback_data: dict
    ):
        message = call.message
        role = (await state.get_data())["role"]
        day_of_week = callback_data["data"]
        # FIX: format
        if await is_find_for_student(state):
            text = await get_user_day_of_week(
                telegram_id=message.chat.id,
                subclass_id=(await state.get_data())["class"],
                day_of_week=day_of_week,
                is_searching=True,
            )
        else:
            text = await get_user_day_of_week(
                telegram_id=message.chat.id,
                teacher_id=(await state.get_data())["teacher"],
                day_of_week=day_of_week,
                is_searching=True,
            )

        await dispatcher_menu(message, role, text)
        await call.answer()

    # =============================
    @dp.callback_query_handler(
        cf.filter(action=["next_lesson"]),
        state=[States.find_menu],
    )
    async def find_next_lesson_handler(
        call: CallbackQuery, state: FSMContext, callback_data: dict
    ):
        message = call.message
        role = (await state.get_data())["role"]
        day_of_week = callback_data["data"]

        if await is_find_for_student(state):
            text = await get_user_next_lesson(
                telegram_id=message.chat.id,
                subclass_id=(await state.get_data())["class"],
                is_searching=True,
            )
        else:
            text = await get_user_next_lesson(
                telegram_id=message.chat.id,
                teacher_id=(await state.get_data())["teacher"],
                is_searching=True,
            )

        await dispatcher_menu(message, role, text)
        await call.answer()

    # =============================
    @dp.callback_query_handler(
        cf.filter(action=["today"]),
        state=[States.find_menu],
    )
    async def find_today_handler(
        call: CallbackQuery, state: FSMContext, callback_data: dict
    ):
        logger.debug(f"{await state.get_data()}")
        message = call.message
        role = (await state.get_data())["role"]

        if await is_find_for_student(state):
            text = await get_user_today(
                telegram_id=message.chat.id,
                subclass_id=(await state.get_data())["find_subclass_id"],
                is_searching=True,
            )
        else:
            text = await get_user_today(
                telegram_id=message.chat.id,
                teacher_id=(await state.get_data())["find_teacher_id"],
                is_searching=True,
            )

        await dispatcher_menu(message, role, text)
        await call.answer()

    # =============================
    @dp.callback_query_handler(
        cf.filter(action=["tomorrow"]),
        state=[States.find_menu],
    )
    async def find_tomorrow_handler(
        call: CallbackQuery, state: FSMContext, callback_data: dict
    ):
        message = call.message
        role = (await state.get_data())["role"]

        if await is_find_for_student(state):
            text = await get_user_tomorrow(
                telegram_id=message.chat.id,
                subclass_id=(await state.get_data())["find_subclass_id"],
                is_searching=True,
            )
        else:
            text = await get_user_tomorrow(
                telegram_id=message.chat.id,
                teacher_id=(await state.get_data())["find_teacher_id"],
                is_searching=True,
            )

        await dispatcher_menu(message, role, text)
        await call.answer()

    # =============================
    @dp.callback_query_handler(
        cf.filter(action=["week"]),
        state=[States.find_menu],
    )
    async def find_week_handler(
        call: CallbackQuery, state: FSMContext, callback_data: dict
    ):
        message = call.message
        role = (await state.get_data())["role"]
        logger.debug(f"{await state.get_data()}")
        if await is_find_for_student(state):
            text = await get_user_week(
                telegram_id=message.chat.id,
                subclass_id=(await state.get_data())["find_subclass_id"],
                is_searching=True,
            )
        else:
            text = await get_user_week(
                telegram_id=message.chat.id,
                teacher_id=(await state.get_data())["find_teacher_id"],
                is_searching=True,
            )

        await dispatcher_menu(message, role, text)
        await call.answer()

    # =============================
    @dp.callback_query_handler(
        cf.filter(action=["find_teacher"]),
        state=[
            States.child_misc_menu_first,
            States.student_misc_menu_first,
            States.teacher_misc_menu_first,
            States.administration_menu_first,
            States.find_teacher_submit,
        ],
    )
    async def find_enter_teacher_handler(
        call: CallbackQuery, state: FSMContext, callback_data: dict
    ):
        await States.find_input_teacher.set()
        await state.update_data({"find_subclass_id": None})
        await state.update_data({"find_teacher_id": None})
        message = call.message
        text = Texts.enter_name
        await send_message(message, text=text, keyboard=None, parse_mode="markdown")
        await call.answer()

    # =============================
    @dp.message_handler(
        lambda message: True,  # TODO add re magic #
        state=[States.find_input_teacher],
    )
    async def find_choose_teacher_handler(message: Message, state: FSMContext):
        await States.find_choose_teacher.set()
        await message.answer(
            "choose from:",
            reply_markup=await find_get_teachers_keyboard(
                message.text, await get_school_id(message.chat.id)
            ),
        )

    # =============================
    @dp.callback_query_handler(
        cf.filter(action=["find_choose_teacher"]),
        state=[States.find_choose_teacher],
    )
    async def find_input_teacher_handler(
        call: CallbackQuery, state: FSMContext, callback_data: dict
    ):
        await States.find_teacher_submit.set()
        message = call.message
        text = Texts.confirm_teacher_from_list.format(
            teacher_name=callback_data["data"]
        )
        await state.update_data({"find_teacher_id": callback_data["data"]})
        await send_message(
            message,
            text=text,
            keyboard=FIND_TEACHER_SUBMIT_KEYBOARD,
            parse_mode="markdown",
        )
        await call.answer()
