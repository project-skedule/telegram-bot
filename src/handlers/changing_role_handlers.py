from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, Message
from src.api import (
    get_children,
    get_subclass_by_params,
    is_registered,
    register_administration,
    register_child,
    register_student,
    register_teacher,
    save_to_redis,
)
from src.bot import bot, dp
from src.keyboards import (
    ADD_MORE_CHILDREN_KEYBOARD,
    ADMINISTRATION_MENU_FIRST_KEYBOARD,
    CHOOSE_ROLE_KEYBOARD,
    STUDENT_MAIN_KEYBOARD,
    STUDENT_SUBMIT_KEYBOARD,
    SUBMIT_ADMINISTRATION_KEYBOARD,
    TEACHER_MAIN_KEYBOARD,
    TEACHER_SUBMIT_KEYBOARD,
    cf,
    generate_markup,
    get_child_keyboard,
    get_enter_group_keyboard,
    get_enter_letter_keyboard,
    get_enter_parallel_keyboard,
    get_schools_keyboard,
    get_teachers_keyboard,
)
from src.logger import logger
from src.redis import get_school_id
from src.some_functions import send_message, is_changing_role
from src.states import States
from src.texts import Texts


async def register_changing_role_handlers():
    @dp.callback_query_handler(
        cf.filter(action=["registration"]),
        state=[
            States.student_misc_menu_second,
            States.teacher_misc_menu_second,
            States.administration_menu_second,
        ],
    )
    async def changing_role(call: CallbackQuery, state: FSMContext):
        message = call.message
        logger.debug("role change")
        await state.set_data({"changed": True})
        await States.choose_role.set()
        await message.answer(
            text=Texts.greeting + "TODO",
            reply_markup=CHOOSE_ROLE_KEYBOARD,
            parse_mode="markdown",
        )

    # ============================
    @dp.callback_query_handler(
        cf.filter(action=["choose_role"]),
        state=[
            States.show_childs,
            States.input_school,
            States.administration_menu_second,
            States.parent_misc_menu_first,
            States.student_misc_menu_second,
            States.teacher_misc_menu_second,
            States.administration_submit,
        ],
    )
    async def choose_role_handler(
        call: CallbackQuery, state: FSMContext, callback_data: dict
    ):
        logger.debug("choose role")
        await States.choose_role.set()
        message = call.message
        await send_message(
            message,
            text="choose role",
            keyboard=CHOOSE_ROLE_KEYBOARD,
            parse_mode="markdown",
        )
        await call.answer()

    # =============================
    @dp.callback_query_handler(
        cf.filter(action=["input_school"]),
        state=[
            States.choose_role,
            States.show_childs,
        ],
    )
    async def input_school_handler(
        call: CallbackQuery, state: FSMContext, callback_data: dict
    ):
        logger.debug("input school")
        await States.input_school.set()
        # if (await state.get_data()).get("role") is None:
        if await is_changing_role(state):
            await state.update_data({"role": callback_data["data"]})
        message = call.message
        await send_message(
            message,
            text="input school",
            keyboard=None,
            parse_mode="markdown",
        )
        await call.answer()

    # =============================
    @dp.message_handler(
        lambda message: True,  # TODO add re magic
        state=[States.input_school],
    )
    async def input_school_message(message: Message):
        logger.debug(f"input school message: {message.text}")
        await States.choose_school.set()
        await message.answer(
            text=f"school like {message.text}",  # FIX: add format for schools like entered
            reply_markup=(await get_schools_keyboard(message.text)),
            parse_mode="markdown",
        )

    # =============================
    @dp.callback_query_handler(
        cf.filter(action=["choose_school"]),
        state=[States.choose_school],
    )
    async def choose_school_handler(
        call: CallbackQuery, state: FSMContext, callback_data: dict
    ):
        logger.debug(f"choose school")
        role = (await state.get_data())["role"]

        message = call.message
        await state.update_data({"school": callback_data["data"]})

        if role in ["Parent", "Student"]:
            await States.enter_parallel.set()
            await send_message(
                message,
                text=Texts.enter_parallel,
                keyboard=(await get_enter_parallel_keyboard(message.chat.id)),
                parse_mode="markdown",
            )

        elif role == "Teacher":
            await States.input_teacher.set()
            await send_message(
                message,
                text=Texts.enter_name,
                keyboard=None,
                parse_mode="markdown",
            )
        elif role == "Administration":
            await States.administration_submit.set()
            text = Texts.confirm_for_admin.format(
                school_name=(await state.get_data())["school"]
            )
            await send_message(
                message,
                text=text,
                keyboard=SUBMIT_ADMINISTRATION_KEYBOARD,
                parse_mode="markdown",
            )

        await call.answer()

    # ! =============================
    @dp.message_handler(
        # lambda message: True,  # TODO add re magick #
        state=[States.input_teacher],
    )
    async def choose_teacher_handler(message: Message, state: FSMContext):
        logger.debug(f"choose teacher")
        await States.choose_teacher.set()
        await message.answer(
            text="Choose teacher ",  # FIX: text for choosing teacher from list
            reply_markup=await get_teachers_keyboard(
                message.text, await get_school_id(message.chat.id)
            ),
            parse_mode="markdown",
        )

    # =============================
    @dp.callback_query_handler(
        cf.filter(action=["choose_teacher"]),
        state=[States.choose_teacher],
    )
    async def input_teacher_handler(
        call: CallbackQuery, state: FSMContext, callback_data: dict
    ):
        logger.debug(f"input teacher")
        await States.teacher_submit.set()
        message = call.message
        text = Texts.confirm_teacher_from_list.format(
            teacher_name=callback_data["data"]
        )
        await state.update_data({"teacher": callback_data["data"]})
        await send_message(
            message,
            text=text,
            keyboard=TEACHER_SUBMIT_KEYBOARD,
            parse_mode="markdown",
        )
        await call.answer()

    # =============================
    @dp.callback_query_handler(
        cf.filter(action=["enter_parallel"]),
        state=[States.student_submit],
    )
    async def enter_parallel_handler(
        call: CallbackQuery, state: FSMContext, callback_data: dict
    ):
        logger.debug(f"enter parallel")
        message = call.message
        await States.enter_parallel.set()
        await send_message(
            message,
            text=Texts.enter_parallel,
            keyboard=(await get_enter_parallel_keyboard(message.chat.id)),
            parse_mode="markdown",
        )
        await call.answer()

    # =============================
    @dp.callback_query_handler(
        cf.filter(action=["enter_letter"]),
        state=[States.enter_parallel],
    )
    async def enter_letter_handler(
        call: CallbackQuery, state: FSMContext, callback_data: dict
    ):
        logger.debug(f"enter letter")
        await States.enter_letter.set()
        parallel = callback_data["data"]
        await state.update_data({"parallel": f"{parallel}"})
        message = call.message
        await send_message(
            message,
            text=Texts.enter_letter,
            keyboard=(await get_enter_letter_keyboard(message.chat.id, parallel)),
            parse_mode="markdown",
        )
        await call.answer()

    # =============================
    @dp.callback_query_handler(
        cf.filter(action=["enter_group"]),
        state=[States.enter_letter],
    )
    async def enter_group_handler(
        call: CallbackQuery, state: FSMContext, callback_data: dict
    ):
        logger.debug(f"enter group")
        await States.enter_group.set()
        parallel = (await state.get_data())["parallel"]
        letter = callback_data["data"]
        await state.update_data({"letter": f"{letter}"})
        message = call.message
        await send_message(
            message,
            text=Texts.enter_group,
            keyboard=(
                await get_enter_group_keyboard(message.chat.id, parallel, letter)
            ),
            parse_mode="markdown",
        )
        await call.answer()

    # =============================
    @dp.callback_query_handler(
        cf.filter(action=["student_submit"]),
        state=[States.enter_group],
    )
    async def student_submit_handler(
        call: CallbackQuery, state: FSMContext, callback_data: dict
    ):
        logger.debug(f"submit student")
        await States.student_submit.set()
        await state.update_data({"group": f"{callback_data['data']}"})
        message = call.message
        parallel = (await state.get_data())["parallel"]
        letter = (await state.get_data())["letter"]
        group = (await state.get_data())["group"]
        await send_message(
            message,
            text=Texts.confirm_class.format(subclass=parallel + letter + group),
            keyboard=STUDENT_SUBMIT_KEYBOARD,
            parse_mode="markdown",
        )

        await call.answer()

    # =============================
    @dp.callback_query_handler(
        cf.filter(action=["student_submit_yes"]),
        state=[States.student_submit],
    )
    async def student_submit_yes_handler(
        call: CallbackQuery, state: FSMContext, callback_data: dict
    ):
        message = call.message

        parallel = (await state.get_data())["parallel"]
        letter = (await state.get_data())["letter"]
        group = (await state.get_data())["group"]
        school = (await state.get_data())["school"]

        subclass_id = await get_subclass_by_params(school, parallel, letter, group)
        await state.update_data({"subclass_id": subclass_id})

        role = (await state.get_data())["role"]
        if role == "Parent":
            await register_child(telegram_id=message.chat.id, subclass_id=subclass_id)
            await States.show_childs.set()
            children = await get_children(message.chat.id)
            await send_message(
                message,
                text="\n".join(children.keys())
                + "\nwanna more?",  # FIX: children names from redis
                keyboard=ADD_MORE_CHILDREN_KEYBOARD,
                parse_mode="markdown",
            )
        elif role == "Student":
            (await state.get_data())["school"]
            await register_student(telegram_id=message.chat.id, subclass_id=subclass_id)
            await States.student_menu.set()
            await send_message(
                message,
                text="student menu",
                keyboard=STUDENT_MAIN_KEYBOARD,
                parse_mode="markdown",
            )

        await call.answer()

    # =============================
    @dp.callback_query_handler(
        cf.filter(action=["show_childs"]),
        state=[States.choose_child, States.choose_role],
    )
    async def show_children_handler(
        call: CallbackQuery, state: FSMContext, callback_data: dict
    ):
        message = call.message
        await States.show_childs.set()
        await state.update_data({"role": "Parent"})
        children = await get_children(message.chat.id)
        await send_message(
            message,
            text="\n".join(children.keys())
            + "\nwanna more?",  # FIX: children names from redis
            keyboard=ADD_MORE_CHILDREN_KEYBOARD,
            parse_mode="markdown",
        )
        await call.answer()

    # =============================
    @dp.callback_query_handler(
        cf.filter(action=["teacher_menu"]),
        state=[States.teacher_submit],
    )
    async def submit_teacher_yes_handler(
        call: CallbackQuery, state: FSMContext, callback_data: dict
    ):
        message = call.message
        await States.teacher_menu.set()
        school = (await state.get_data())["school"]
        teacher = (await state.get_data())["teacher"]
        await register_teacher(telegram_id=message.chat.id, teacher_id=teacher)
        await send_message(
            message,
            text=Texts.successful_reg_teacher.format(teacher_name=teacher),
            keyboard=TEACHER_MAIN_KEYBOARD,
            parse_mode="markdown",
        )
        await call.answer()

    # =============================
    @dp.callback_query_handler(
        cf.filter(action=["administration_menu_first"]),
        state=[States.administration_submit],
    )
    async def submit_administration_yes_handler(
        call: CallbackQuery, state: FSMContext, callback_data: dict
    ):
        message = call.message
        await States.administration_menu_first.set()
        school = (await state.get_data())["school"]
        await register_administration(telegram_id=message.chat.id, school_id=school)
        await send_message(
            message,
            text=Texts.successful_reg_admin.format(school_name=school),
            keyboard=ADMINISTRATION_MENU_FIRST_KEYBOARD,
            parse_mode="markdown",
        )
        await call.answer()
