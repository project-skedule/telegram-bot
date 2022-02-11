from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, Message
from src.api import (
    change_role,
    get_children,
    get_school_name_by_id,
    get_subclass_by_params,
    get_teacher_name_by_id,
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
    BACK_FROM_INPUT_SCHOOL_KEYBOARD,
    BACK_FROM_INPUT_TEACHER_NAME_KEYBOARD,
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
from src.some_functions import is_changing_role, send_message
from src.states import States
from src.texts import Texts


async def register_registration_handlers():
    @dp.message_handler(
        state="*",
        commands=["start"],
    )
    async def registration_message(message: Message, state: FSMContext):
        logger.debug("/start")
        logger.debug(f"{await state.get_data()}")
        if not await is_registered(message.chat.id):
            await States.choose_role.set()
            await message.answer(
                text=Texts.greeting,
                reply_markup=CHOOSE_ROLE_KEYBOARD,
                parse_mode="markdown",
            )
        else:  # TODO add dump to redis from api here (because of role changes (or redis breaks))
            await save_to_redis(message.chat.id)
            data = await state.get_data()
            role = data["role"]
            if role == "Parent":
                await message.answer(
                    text=Texts.choose_children,
                    reply_markup=await get_child_keyboard(message.chat.id),
                    parse_mode="markdown",
                )
                await States.choose_child.set()
            elif role == "Student":
                await message.answer(
                    text=Texts.student_main_menu,
                    reply_markup=STUDENT_MAIN_KEYBOARD,
                    parse_mode="markdown",
                )
                await States.student_menu.set()
            elif role == "Teacher":
                await message.answer(
                    text=Texts.teacher_main_menu,
                    reply_markup=TEACHER_MAIN_KEYBOARD,
                    parse_mode="markdown",
                )
                await States.teacher_menu.set()
            elif role == "Administration":
                await message.answer(
                    text=Texts.admin_main_menu,
                    reply_markup=ADMINISTRATION_MENU_FIRST_KEYBOARD,
                    parse_mode="markdown",
                )
                await States.administration_menu_first.set()

    # =============================
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
        await send_message(
            message=message,
            text=Texts.choose_role,
            keyboard=CHOOSE_ROLE_KEYBOARD,
            parse_mode="markdown",
        )

        await call.answer()
        await States.choose_role.set()

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
            States.input_school,
        ],
    )
    async def choose_role_handler(
        call: CallbackQuery, state: FSMContext, callback_data: dict
    ):
        logger.debug("choose role")
        message = call.message
        await send_message(
            message,
            text=Texts.choose_role,
            keyboard=CHOOSE_ROLE_KEYBOARD,
            parse_mode="markdown",
        )
        await call.answer()
        await States.choose_role.set()

    # =============================
    @dp.callback_query_handler(
        cf.filter(action=["input_school"]),
        state=[States.choose_role, States.show_childs, States.choose_school],
    )
    async def input_school_handler(
        call: CallbackQuery, state: FSMContext, callback_data: dict
    ):
        logger.debug("input school")
        if callback_data["data"] != "0":  # back button
            await state.update_data({"role": callback_data["data"]})
        message = call.message
        await send_message(
            message,
            text=Texts.enter_school_name,
            keyboard=BACK_FROM_INPUT_SCHOOL_KEYBOARD,
            parse_mode="markdown",
        )
        await call.answer()
        await States.input_school.set()

    # =============================
    @dp.message_handler(
        state=[States.input_school],
    )
    async def input_school_message(message: Message, state: FSMContext):
        logger.debug(f"input school message: {message.text}")
        await message.answer(
            text=Texts.select_school_name,
            reply_markup=(await get_schools_keyboard(message.text)),
            parse_mode="markdown",
        )
        await state.update_data({"user_school_input": message.text})
        await States.choose_school.set()

    # =============================
    @dp.callback_query_handler(
        cf.filter(action=["show_schools"]),
        state=[States.enter_parallel, States.input_teacher],
    )
    async def show_schools_handler(  # equivalent to input_school_message
        call: CallbackQuery, state: FSMContext, callback_data: dict
    ):
        message = call.message
        await send_message(
            message,
            text=Texts.select_school_name,
            keyboard=await get_schools_keyboard(
                (await state.get_data())["user_school_input"]
            ),
            parse_mode="markdown",
        )
        await call.answer()
        await States.choose_school.set()

    # =============================
    @dp.callback_query_handler(
        cf.filter(action=["choose_school"]),
        state=[
            States.choose_school,
            States.enter_letter,
            States.choose_teacher,
            States.teacher_submit,
        ],
    )
    async def choose_school_handler(
        call: CallbackQuery, state: FSMContext, callback_data: dict
    ):
        logger.debug(f"choose school")
        role = (await state.get_data())["role"]
        message = call.message

        if callback_data["data"] != "None":
            school = callback_data["data"]
            school_name = await get_school_name_by_id(school)

            await state.update_data(
                {
                    "school": school,
                    "school_name": school_name,
                }
            )

        if role == "Student":
            await send_message(
                message,
                text=Texts.enter_parallel_on_register_student,
                keyboard=(await get_enter_parallel_keyboard(message.chat.id)),
                parse_mode="markdown",
            )
            await States.enter_parallel.set()

        elif role == "Parent":
            await send_message(
                message,
                text=Texts.enter_parallel_on_register_parent,
                keyboard=(await get_enter_parallel_keyboard(message.chat.id)),
                parse_mode="markdown",
            )
            await States.enter_parallel.set()

        elif role == "Teacher":
            await send_message(
                message,
                text=Texts.enter_name_on_register,
                keyboard=BACK_FROM_INPUT_TEACHER_NAME_KEYBOARD,
                parse_mode="markdown",
            )
            await States.input_teacher.set()
        elif role == "Administration":
            text = Texts.confirm_for_admin.format(
                school_name=(await state.get_data())["school_name"]
            )
            await send_message(
                message,
                text=text,
                keyboard=SUBMIT_ADMINISTRATION_KEYBOARD,
                parse_mode="markdown",
            )
            await States.administration_submit.set()

        await call.answer()

    # ! =============================
    @dp.message_handler(
        state=[States.input_teacher],
    )
    async def choose_teacher_handler(message: Message, state: FSMContext):
        logger.debug("choose teacher")
        await message.answer(
            text=Texts.select_teacher_from_list,
            reply_markup=await get_teachers_keyboard(
                message.text, await get_school_id(message.chat.id)
            ),
            parse_mode="markdown",
        )
        await States.choose_teacher.set()

    # =============================
    @dp.callback_query_handler(
        cf.filter(action=["choose_teacher"]),
        state=[States.choose_teacher],
    )
    async def input_teacher_handler(
        call: CallbackQuery, state: FSMContext, callback_data: dict
    ):
        logger.debug("input teacher")
        message = call.message
        teacher = callback_data["data"]
        teacher_name = await get_teacher_name_by_id(teacher)

        text = Texts.confirm_name.format(teacher_name=teacher_name)
        await state.update_data(
            {
                "teacher": teacher,
                "teacher_name": teacher_name,
            }
        )
        await send_message(
            message,
            text=text,
            keyboard=TEACHER_SUBMIT_KEYBOARD,
            parse_mode="markdown",
        )
        await call.answer()
        await States.teacher_submit.set()

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
        await send_message(
            message,
            text=Texts.enter_parallel,
            keyboard=(await get_enter_parallel_keyboard(message.chat.id)),
            parse_mode="markdown",
        )
        await call.answer()
        await States.enter_parallel.set()

    # =============================
    @dp.callback_query_handler(
        cf.filter(action=["enter_letter"]),
        state=[States.enter_parallel, States.enter_group],
    )
    async def enter_letter_handler(
        call: CallbackQuery, state: FSMContext, callback_data: dict
    ):
        logger.debug(f"enter letter")
        message = call.message
        if callback_data["data"] != "None":
            parallel = callback_data["data"]
            await state.update_data({"parallel": f"{parallel}"})

        parallel = (await state.get_data())["parallel"]
        await send_message(
            message,
            text=Texts.enter_letter,
            keyboard=(await get_enter_letter_keyboard(message.chat.id, parallel)),
            parse_mode="markdown",
        )
        await call.answer()
        await States.enter_letter.set()

    # =============================
    @dp.callback_query_handler(
        cf.filter(action=["enter_group"]),
        state=[States.enter_letter],
    )
    async def enter_group_handler(
        call: CallbackQuery, state: FSMContext, callback_data: dict
    ):
        logger.debug(f"enter group")
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
        await States.enter_group.set()

    # =============================
    @dp.callback_query_handler(
        cf.filter(action=["student_submit"]),
        state=[States.enter_group],
    )
    async def student_submit_handler(
        call: CallbackQuery, state: FSMContext, callback_data: dict
    ):
        logger.debug(f"submit student")
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
        await States.student_submit.set()

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
            children = await get_children(message.chat.id)
            await send_message(
                message,
                text="\n".join(children.keys())
                + "\nwanna more?",  # FIX: children names from redis
                keyboard=ADD_MORE_CHILDREN_KEYBOARD,
                parse_mode="markdown",
            )
            await States.show_childs.set()
        elif role == "Student":
            (await state.get_data())["school"]
            if (await state.get_data()).get("changed") is None:
                await register_student(
                    telegram_id=message.chat.id, subclass_id=subclass_id
                )
            else:
                await change_role(telegram_id=message.chat.id, subclass_id=subclass_id)
                await save_to_redis(message.chat.id)
                await state.update_data({"changed": None})

            await send_message(
                message,
                text=Texts.successful_reg_student.format(
                    subclass=f"{parallel}{letter}{group}"
                ),
                keyboard=STUDENT_MAIN_KEYBOARD,
                parse_mode="markdown",
            )
            await States.student_menu.set()

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
        await States.show_childs.set()

    # =============================
    @dp.callback_query_handler(
        cf.filter(action=["teacher_menu"]),
        state=[States.teacher_submit],
    )
    async def submit_teacher_yes_handler(
        call: CallbackQuery, state: FSMContext, callback_data: dict
    ):
        message = call.message
        school = (await state.get_data())["school"]
        teacher_id = (await state.get_data())["teacher"]
        teacher_name = (await state.get_data())["teacher_name"]
        if (await state.get_data()).get("changed") is None:
            await register_teacher(telegram_id=message.chat.id, teacher_id=teacher_id)

        else:
            await change_role(telegram_id=message.chat.id, teacher_id=teacher_id)
            await save_to_redis(message.chat.id)
            await state.update_data({"changed": None})

        await send_message(
            message,
            text=Texts.successful_reg_teacher.format(teacher_name=teacher_name),
            keyboard=TEACHER_MAIN_KEYBOARD,
            parse_mode="markdown",
        )
        await call.answer()
        await States.teacher_menu.set()

    # =============================
    @dp.callback_query_handler(
        cf.filter(action=["administration_menu_first"]),
        state=[States.administration_submit],
    )
    async def submit_administration_yes_handler(
        call: CallbackQuery, state: FSMContext, callback_data: dict
    ):
        message = call.message
        school_id = (await state.get_data())["school"]
        school_name = (await state.get_data())["school_name"]
        if (await state.get_data()).get("changed") is None:
            await register_administration(
                telegram_id=message.chat.id, school_id=school_id
            )
        else:
            await change_role(telegram_id=message.chat.id, school_id=school_id)
            await save_to_redis(message.chat.id)
            await state.update_data({"changed": None})
        await send_message(
            message,
            text=Texts.successful_reg_admin.format(school_name=school_name),
            keyboard=ADMINISTRATION_MENU_FIRST_KEYBOARD,
            parse_mode="markdown",
        )
        await call.answer()
        await States.administration_menu_first.set()
