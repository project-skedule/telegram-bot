from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, Message
from src.api import (
    get_subclass_by_params,
    get_teacher_name_by_id,
    get_user_day_of_week,
    get_user_today,
    get_user_tomorrow,
    get_user_week,
)
from src.bot import dp
from src.keyboards import (
    BACK_FROM_FIND_TEACHER_KEYBOARD,
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
from loguru import logger
from src.redis import get_school_id
from src.some_functions import dispatcher_menu, is_find_for_student, send_message
from src.states import States
from src.texts import Texts


async def register_find_handlers():
    @dp.callback_query_handler(
        cf.filter(action=["find_class"]),
        state=[
            States.student_menu,
            States.teacher_menu,
            States.administration_menu_first,
            States.find_student_submit,
            States.find_enter_letter,
        ],
    )
    async def find_class_handler(call: CallbackQuery, state: FSMContext):
        await state.update_data({"find_subclass_id": None})
        await state.update_data({"find_teacher_id": None})

        message = call.message
        role = (await state.get_data())["role"]
        if await state.get_state() == States.find_enter_letter:
            logger.info(
                f"{message.chat.id}| {message.chat.username} | {role} | find_class | back_find_choose_letter_button"
            )
        elif await state.get_state() == States.find_student_submit:
            logger.info(
                f"{message.chat.id}| {message.chat.username} | {role} | find_class | back_find_student_submit_button"
            )
        else:
            logger.info(
                f"{message.chat.id}| {message.chat.username} | {role} | find_class | find_class_button"
            )

        await send_message(
            message,
            text=Texts.enter_parallel,
            keyboard=await get_find_enter_parallel_keyboard(message.chat.id),
        )
        await call.answer()
        await States.find_enter_parallel.set()

    # =============================
    @dp.callback_query_handler(
        cf.filter(action=["find_enter_letter"]),
        state=[States.find_enter_parallel, States.find_enter_group],
    )
    async def find_enter_letter_handler(
        call: CallbackQuery, state: FSMContext, callback_data: dict
    ):
        role = (await state.get_data())["role"]

        if callback_data["data"] != "None":
            logger.info(
                f"{message.chat.id}| {message.chat.username} | {role} | find_enter_letter | find_parallel_button"
            )
            parallel = callback_data["data"]
            await state.update_data({"find_parallel": f"{parallel}"})
        else:
            logger.info(
                f"{message.chat.id}| {message.chat.username} | {role} | find_enter_letter | back_find_enter_group_button"
            )
        parallel = (await state.get_data())["find_parallel"]
        message = call.message
        await send_message(
            message,
            text=Texts.enter_letter,
            keyboard=await get_find_enter_letter_keyboard(message.chat.id, parallel),
        )
        await call.answer()
        await States.find_enter_letter.set()

    # =============================
    @dp.callback_query_handler(
        cf.filter(action=["find_enter_group"]),
        state=[States.find_enter_letter],
    )
    async def find_enter_group_handler(
        call: CallbackQuery, state: FSMContext, callback_data: dict
    ):
        message = call.message
        role = (await state.get_data())["role"]

        logger.info(
            f"{message.chat.id}| {message.chat.username} | {role} | find_enter_group | find_letter_button"
        )

        parallel = (await state.get_data())["find_parallel"]
        letter = callback_data["data"]
        await state.update_data({"find_letter": letter})
        await send_message(
            message,
            text=Texts.enter_group,
            keyboard=await get_find_enter_group_keyboard(
                message.chat.id, parallel, letter
            ),
        )
        await call.answer()
        await States.find_enter_group.set()

    # =============================
    @dp.callback_query_handler(
        cf.filter(action=["find_student_submit"]),
        state=[States.find_enter_group],
    )
    async def find_student_submit_handler(
        call: CallbackQuery, state: FSMContext, callback_data: dict
    ):
        message = call.message
        role = (await state.get_data())["role"]
        logger.info(
            f"{message.chat.id}| {message.chat.username} | {role} | find_student_submit | find_group_button"
        )
        await state.update_data({"find_group": callback_data["data"]})
        parallel = (await state.get_data())["find_parallel"]
        letter = (await state.get_data())["find_letter"]
        group = (await state.get_data())["find_group"]
        subclass_id = await get_subclass_by_params(
            await get_school_id(message.chat.id), parallel, letter, group
        )
        await state.update_data({"find_subclass_id": subclass_id})
        await state.update_data({"find_subclass_name": parallel + letter + group})
        await send_message(
            message,
            text=Texts.confirm_another_class.format(
                subclass=f"{parallel}{letter}{group}"
            ),
            keyboard=FIND_STUDENT_SUBMIT_KEYBOARD,
            parse_mode="Markdown",
        )

        await call.answer()
        await States.find_student_submit.set()

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
        message = call.message
        role = (await state.get_data())["role"]

        if await is_find_for_student(state):
            if await state.get_state() == States.find_day_of_week:
                logger.info(
                    f"{message.chat.id}| {message.chat.username} | {role} | find_student_menu | find_student_back_day_of_week_button"
                )
            else:
                logger.info(
                    f"{message.chat.id}| {message.chat.username} | {role} | find_student_menu | find_submit_student_yes_button"
                )
            text = f"Расписание ученика *{(await state.get_data())['find_subclass_name']}* класса"
        else:
            if await state.get_state() == States.find_day_of_week:
                logger.info(
                    f"{message.chat.id}| {message.chat.username} | {role} | find_teacher_menu | find_teacher_back_day_of_week_button"
                )
            else:
                logger.info(
                    f"{message.chat.id}| {message.chat.username} | {role} | find_teacher_menu | find_submit_teacher_yes_button"
                )

            text = (
                f"Расписание учителя *{(await state.get_data())['find_teacher_name']}*"
            )

        await send_message(
            message,
            text=text,
            keyboard=FIND_MAIN_KEYBOARD,
            parse_mode="markdown",
        )
        await call.answer()
        await States.find_menu.set()

    # =============================
    @dp.callback_query_handler(
        cf.filter(action=["find_day_of_week"]),
        state=[States.find_menu],
    )
    async def find_day_of_week_handler(
        call: CallbackQuery, state: FSMContext, callback_data: dict
    ):
        message = call.message
        role = (await state.get_data())["role"]

        if await is_find_for_student(state):
            logger.info(
                f"{message.chat.id}| {message.chat.username} | {role} | find_student_day_of_week_menu | find_menu_student_button"
            )
        else:
            logger.info(
                f"{message.chat.id}| {message.chat.username} | {role} | find_teacher_day_of_week_menu | find_menu_teacher_button"
            )

        await send_message(
            message,
            text=Texts.select_day_of_week,
            keyboard=FIND_DAY_OF_WEEK_KEYBOARD,
            parse_mode="markdown",
        )
        await call.answer()
        await States.find_day_of_week.set()

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

        if await is_find_for_student(state):
            logger.info(
                f"{message.chat.id}| {message.chat.username} | {role} | find_student_day_of_week | find_menu_student_day_of_week_button"
            )
        else:
            logger.info(
                f"{message.chat.id}| {message.chat.username} | {role} | find_teacher_day_of_week | find_menu_teacher_day_of_week_button"
            )

        day_of_week = int(callback_data["data"])
        if await is_find_for_student(state):
            text = await get_user_day_of_week(
                telegram_id=message.chat.id,
                subclass_id=(await state.get_data())["find_subclass_id"],
                day_of_week=day_of_week,
                is_searching=True,
            )
        else:
            text = await get_user_day_of_week(
                telegram_id=message.chat.id,
                teacher_id=(await state.get_data())["find_teacher_id"],
                day_of_week=day_of_week,
                is_searching=True,
            )

        await dispatcher_menu(message, role, text, "MarkdownV2")
        await call.answer()

    # =============================
    @dp.callback_query_handler(
        cf.filter(action=["today"]),
        state=[States.find_menu],
    )
    async def find_today_handler(
        call: CallbackQuery, state: FSMContext, callback_data: dict
    ):
        message = call.message
        role = (await state.get_data())["role"]

        if await is_find_for_student(state):
            logger.info(
                f"{message.chat.id}| {message.chat.username} | {role} | find_student_today | find_student_today_button"
            )
            text = await get_user_today(
                telegram_id=message.chat.id,
                subclass_id=(await state.get_data())["find_subclass_id"],
                is_searching=True,
            )
        else:
            logger.info(
                f"{message.chat.id}| {message.chat.username} | {role} | find_teacher_today | find_student_today_button"
            )
            text = await get_user_today(
                telegram_id=message.chat.id,
                teacher_id=(await state.get_data())["find_teacher_id"],
                is_searching=True,
            )

        await dispatcher_menu(message, role, text, "MarkdownV2")
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
            logger.info(
                f"{message.chat.id}| {message.chat.username} | {role} | find_student_tomorrow | find_student_tomorrow_button"
            )
            text = await get_user_tomorrow(
                telegram_id=message.chat.id,
                subclass_id=(await state.get_data())["find_subclass_id"],
                is_searching=True,
            )
        else:
            logger.info(
                f"{message.chat.id}| {message.chat.username} | {role} | find_teacher_tomorrow | find_student_tomorrow_button"
            )
            text = await get_user_tomorrow(
                telegram_id=message.chat.id,
                teacher_id=(await state.get_data())["find_teacher_id"],
                is_searching=True,
            )

        await dispatcher_menu(message, role, text, "MarkdownV2")
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

        if await is_find_for_student(state):
            logger.info(
                f"{message.chat.id}| {message.chat.username} | {role} | find_student_week | find_student_week_button"
            )
            text = await get_user_week(
                telegram_id=message.chat.id,
                subclass_id=(await state.get_data())["find_subclass_id"],
                is_searching=True,
            )
        else:
            logger.info(
                f"{message.chat.id}| {message.chat.username} | {role} | find_teacher_week | find_student_week_button"
            )
            text = await get_user_week(
                telegram_id=message.chat.id,
                teacher_id=(await state.get_data())["find_teacher_id"],
                is_searching=True,
            )

        await dispatcher_menu(message, role, text, "MarkdownV2")
        await call.answer()

    # =============================
    @dp.callback_query_handler(
        cf.filter(action=["find_teacher"]),
        state=[
            States.child_misc_menu_first,
            States.student_menu,
            States.teacher_menu,
            States.administration_menu_first,
            States.find_teacher_submit,
            States.find_choose_teacher,
        ],
    )
    async def find_enter_teacher_handler(
        call: CallbackQuery, state: FSMContext, callback_data: dict
    ):
        message = call.message
        role = (await state.get_data())["role"]

        if await state.get_state() == States.find_choose_teacher:
            logger.info(
                f"{message.chat.id}| {message.chat.username} | {role} | find_teacher | back_find_choose_teacher_button"
            )
        elif await state.get_state() == States.find_teacher_submit:
            logger.info(
                f"{message.chat.id}| {message.chat.username} | {role} | find_teacher | back_find_teacher_submit_button"
            )
        else:
            logger.info(
                f"{message.chat.id}| {message.chat.username} | {role} | find_teacher | find_teacher_button"
            )

        await state.update_data({"find_subclass_id": None})
        await state.update_data({"find_teacher_id": None})
        text = Texts.enter_name
        await send_message(
            message,
            text=text,
            keyboard=BACK_FROM_FIND_TEACHER_KEYBOARD,
            parse_mode="markdown",
        )

        await call.answer()
        await States.find_input_teacher.set()

    # =============================
    @dp.message_handler(
        state=[States.find_input_teacher],
    )
    async def find_input_teacher_handler(message: Message, state: FSMContext):
        role = (await state.get_data())["role"]

        logger.info(
            f"{message.chat.id}| {message.chat.username} | {role} | find_enter_teacher | find_enter_teacher_message"
        )
        
        await message.answer(
            text=Texts.select_teacher_from_list,
            reply_markup=await find_get_teachers_keyboard(
                message.text, await get_school_id(message.chat.id)
            ),
        )

        await States.find_choose_teacher.set()

    # =============================
    @dp.callback_query_handler(
        cf.filter(action=["find_choose_teacher"]),
        state=[States.find_choose_teacher],
    )
    async def find_choose_teacher_handler(
        call: CallbackQuery, state: FSMContext, callback_data: dict
    ):
        message = call.message

        role = (await state.get_data())["role"]

        logger.info(
            f"{message.chat.id}| {message.chat.username} | {role} | find_teacher_submit | find_teacher_name_button"
        )

        teacher_id = callback_data["data"]
        teacher_name = await get_teacher_name_by_id(teacher_id)
        await state.update_data({"find_teacher_id": teacher_id})
        await state.update_data({"find_teacher_name": teacher_name})
        text = Texts.confirm_another_teacher.format(teacher_name=teacher_name)
        await send_message(
            message,
            text=text,
            keyboard=FIND_TEACHER_SUBMIT_KEYBOARD,
            parse_mode="markdown",
        )

        await call.answer()
        await States.find_teacher_submit.set()
