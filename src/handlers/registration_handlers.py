from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, Message
from src.api import (
    change_role,
    get_school_name_by_id,
    get_subclass_by_params,
    get_teacher_name_by_id,
    is_registered,
    register_administration,
    register_child,
    register_parent,
    register_student,
    register_teacher,
    save_to_redis,
)
from src.bot import dp
from src.keyboards import (
    ADD_MORE_CHILDREN_KEYBOARD,
    ADMINISTRATION_MENU_FIRST_KEYBOARD,
    BACK_FROM_INPUT_SCHOOL_KEYBOARD,
    BACK_FROM_INPUT_TEACHER_NAME_KEYBOARD,
    CHOOSE_ROLE_KEYBOARD,
    STUDENT_MAIN_KEYBOARD,
    STUDENT_SUBMIT_KEYBOARD,
    SUBMIT_ADMINISTRATION_KEYBOARD,
    SUBMIT_CHILD_NAME_KEYBOARD,
    SUBMIT_PARENT_REGISTRATION_KEYBOARD,
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
from loguru import logger
from src.redis import get_premium_status, get_school_id, get_children
from src.some_functions import send_message
from src.states import States
from src.texts import Texts


async def register_registration_handlers():
    @dp.message_handler(
        state="*",
        commands=["start"],
    )
    async def registration_message(message: Message, state: FSMContext):
        if not await is_registered(message.chat.id):
            logger.info(
                f"{message.chat.id} | {message.chat.username} | None | /start | start_command"
            )
            await message.answer(
                text=Texts.greeting,
                reply_markup=CHOOSE_ROLE_KEYBOARD,
                parse_mode="markdown",
            )
            await States.choose_role.set()
        else:
            await save_to_redis(message.chat.id)
            data = await state.get_data()
            role = data.get("role")
            logger.info(
                f"{message.chat.id} | {message.chat.username} | {role} | /start | start_command"
            )
            if role == "Parent":
                await message.answer(
                    text=Texts.choose_children,
                    reply_markup=await get_child_keyboard(message.chat.id),
                    parse_mode="markdown",
                )
                await States.show_childs.set()
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
            States.parent_misc_menu_first,
        ],
    )
    async def changing_role(call: CallbackQuery, state: FSMContext):
        await state.set_data({"changed": True})
        message = call.message
        logger.info(
            f"{message.chat.id} | {message.chat.username} | None | registration | change_role_button"
        )
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
            States.register_parent,
        ],
    )
    async def choose_role_handler(
        call: CallbackQuery, state: FSMContext, callback_data: dict
    ):
        message = call.message
        role = (await state.get_data()).get("role")
        logger.info(
            f"{message.chat.id} | {message.chat.username} | {role} | registration | change_role_button"
        )
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
        state=[
            States.choose_role,
            States.choose_school,
            States.submit_child_name,
        ],
    )
    async def input_school_handler(
        call: CallbackQuery, state: FSMContext, callback_data: dict
    ):
        message = call.message
        role = (await state.get_data()).get("role")
        last_state = await state.get_state()
        if last_state == States.choose_role:
            logger.info(
                f"{message.chat.id} | {message.chat.username} | {role} | input_school | role_button"
            )
        elif last_state == States.choose_school:
            logger.info(
                f"{message.chat.id} | {message.chat.username} | {role} | input_school | back_choose_school_button"
            )
        else:
            logger.info(
                f"{message.chat.id} | {message.chat.username} | {role} | input_school | submit_child_name_no_button"
            )

        if callback_data["data"] != "0":  # back button
            await state.update_data({"role": callback_data["data"]})
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
        role = (await state.get_data()).get("role")
        logger.info(
            f"{message.chat.id} | {message.chat.username} | {role} | show_schools | input_school_message"
        )

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
        role = (await state.get_data()).get("role")
        logger.info(
            f"{message.chat.id} | {message.chat.username} | {role} | show_schools | back_to_show_schools_button"
        )
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
        message = call.message
        role = (await state.get_data()).get("role")

        if callback_data["data"] != "None":
            school = int(callback_data["data"])
            school_name = await get_school_name_by_id(school)

            await state.update_data(
                {
                    "school": school,
                    "school_name": school_name,
                }
            )

        if role == "Student":
            logger.info(
                f"{message.chat.id} | {message.chat.username} | {role} | enter_parallel | school_button"
            )
            await send_message(
                message,
                text=Texts.enter_parallel_on_register_student,
                keyboard=(await get_enter_parallel_keyboard(message.chat.id)),
                parse_mode="markdown",
            )
            await States.enter_parallel.set()

        elif role == "Parent":
            logger.info(
                f"{message.chat.id} | {message.chat.username} | {role} | enter_parallel | school_button"
            )
            await send_message(
                message,
                text=Texts.enter_parallel_on_register_parent,
                keyboard=(await get_enter_parallel_keyboard(message.chat.id)),
                parse_mode="markdown",
            )
            await States.enter_parallel.set()

        elif role == "Teacher":
            logger.info(
                f"{message.chat.id} | {message.chat.username} | {role} | input_teacher | school_button"
            )
            await send_message(
                message,
                text=Texts.enter_name_on_register,
                keyboard=BACK_FROM_INPUT_TEACHER_NAME_KEYBOARD,
                parse_mode="markdown",
            )
            await States.input_teacher.set()
        elif role == "Administration":
            logger.info(
                f"{message.chat.id} | {message.chat.username} | {role} | confirm_administration | school_button"
            )
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
    async def input_teacher_handler(message: Message, state: FSMContext):
        role = (await state.get_data()).get("role")
        logger.info(
            f"{message.chat.id} | {message.chat.username} | {role} | choose_teacher | teacher_name_message"
        )
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
    async def choose_teacher_handler(
        call: CallbackQuery, state: FSMContext, callback_data: dict
    ):
        message = call.message
        role = (await state.get_data()).get("role")
        logger.info(
            f"{message.chat.id} | {message.chat.username} | {role} | teacher_submit | teacher_name_button"
        )
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
        message = call.message
        role = (await state.get_data()).get("role")
        logger.info(
            f"{message.chat.id} | {message.chat.username} | {role} | enter_parallel | student_submit_no_button"
        )
        if role == "Student":
            text = Texts.enter_parallel_on_register_student
        else:
            text = Texts.enter_parallel_on_register_parent
        await send_message(
            message,
            text=text,
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
        message = call.message
        role = (await state.get_data()).get("role")
        if await state.get_state() == States.enter_parallel:
            logger.info(
                f"{message.chat.id} | {message.chat.username} | {role} | enter_letter | parallel_button"
            )
        else:
            logger.info(
                f"{message.chat.id} | {message.chat.username} | {role} | enter_letter | back_group_button"
            )
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
        message = call.message
        role = (await state.get_data()).get("role")
        logger.info(
            f"{message.chat.id} | {message.chat.username} | {role} | enter_group | letter_button"
        )

        parallel = (await state.get_data())["parallel"]
        letter = callback_data["data"]
        await state.update_data({"letter": f"{letter}"})
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
        message = call.message
        role = (await state.get_data()).get("role")
        logger.info(
            f"{message.chat.id} | {message.chat.username} | {role} | student_submit | group_button"
        )

        await state.update_data({"group": f"{callback_data['data']}"})
        role = (await state.get_data())["role"]
        parallel = (await state.get_data())["parallel"]
        letter = (await state.get_data())["letter"]
        group = (await state.get_data())["group"]

        if role == "Student":
            text = Texts.confirm_class.format(subclass=parallel + letter + group)
        else:
            text = Texts.confirm_child_class.format(subclass=parallel + letter + group)

        await send_message(
            message,
            text=text,
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

        role = (await state.get_data()).get("role")

        parallel = (await state.get_data())["parallel"]
        letter = (await state.get_data())["letter"]
        group = (await state.get_data())["group"]
        school = (await state.get_data())["school"]

        subclass_id = await get_subclass_by_params(school, parallel, letter, group)
        await state.update_data({"subclass_id": subclass_id})

        role = (await state.get_data())["role"]
        if role == "Parent":
            logger.info(
                f"{message.chat.id} | {message.chat.username} | {role} | child_submit_yes | child_submit_yes_button"
            )
            await register_child(
                telegram_id=message.chat.id,
                subclass_id=subclass_id,
                name=(await state.get_data())["reg_child_name"],
            )

            await send_message(
                message,
                text=Texts.successful_reg_child.format(
                    child_name=(await state.get_data())["reg_child_name"]
                ),
                keyboard=await get_child_keyboard(message.chat.id),
                parse_mode="markdown",
            )
            await States.show_childs.set()
        elif role == "Student":
            logger.info(
                f"{message.chat.id} | {message.chat.username} | {role} | student_submit_yes | student_submit_yes_button"
            )
            (await state.get_data())["school"]
            if (await state.get_data()).get("changed") is None:
                await register_student(
                    telegram_id=message.chat.id, subclass_id=subclass_id
                )
            else:
                await change_role(telegram_id=message.chat.id, subclass_id=subclass_id)

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
        cf.filter(action=["register_parent"]),
        state=[States.choose_role],
    )
    async def register_parent_handler(
        call: CallbackQuery, state: FSMContext, callback_data: dict
    ):
        message = call.message
        role = (await state.get_data()).get("role")
        logger.info(
            f"{message.chat.id} | {message.chat.username} | {role} | confirm_parent | parent_button"
        )
        await send_message(
            message,
            text=Texts.confirm_reg_parent,
            keyboard=SUBMIT_PARENT_REGISTRATION_KEYBOARD,
            parse_mode="markdown",
        )
        await call.answer()
        await States.register_parent.set()

    # =============================

    @dp.callback_query_handler(
        cf.filter(action=["register_parent_yes"]),
        state=[States.register_parent],
    )
    async def show_children_handler(
        call: CallbackQuery, state: FSMContext, callback_data: dict
    ):
        message = call.message
        role = (await state.get_data()).get("role")
        logger.info(
            f"{message.chat.id} | {message.chat.username} | {role} | confirm_parent_yes | confirm_parent_yes_button"
        )

        if (await state.get_data()).get("changed") is None:
            await register_parent(telegram_id=message.chat.id)
        else:
            await change_role(telegram_id=message.chat.id)

        await send_message(
            message,
            text=Texts.successful_reg_parent,
            keyboard=await get_child_keyboard(message.chat.id),
            parse_mode="markdown",
        )
        await call.answer()
        await States.show_childs.set()

    # =============================
    @dp.callback_query_handler(
        cf.filter(action=["enter_child_name"]),
        state=[States.show_childs, States.submit_child_name],
    )
    async def enter_child_name_handler(
        call: CallbackQuery, state: FSMContext, callback_data: dict
    ):
        message = call.message
        role = (await state.get_data())["role"]
        if await state.get_state() == States.show_childs:
            logger.info(
                f"{message.chat.id} | {message.chat.username} | {role} | enter_child_name | add_child_button"
            )
        else:
            logger.info(
                f"{message.chat.id} | {message.chat.username} | {role} | enter_child_name | submit_child_name_no_button"
            )
        if (
            await get_premium_status(message.chat.id) == 0
            and len(await get_children(message.chat.id)) == 1
        ):
            await send_message(
                message,
                text=Texts.not_enough_premium_children,
                keyboard=await get_child_keyboard(message.chat.id),  # add back button
                parse_mode="markdown",
            )
            await States.show_childs.set()

        else:
            await send_message(
                message,
                text=Texts.enter_child_name,
                keyboard=None,  # add back button
                parse_mode="markdown",
            )
            await States.enter_child_name.set()
        await call.answer()

    # =============================
    @dp.message_handler(
        state=[States.enter_child_name],
    )
    async def submit_child_name_handler(message: Message, state: FSMContext):
        role = (await state.get_data())["role"]
        logger.info(
            f"{message.chat.id} | {message.chat.username} | {role} | submit_child_name | child_name_message"
        )
        await state.update_data({"reg_child_name": message.text})
        await message.answer(
            text=Texts.submit_child_name.format(child_name=message.text),
            reply_markup=SUBMIT_CHILD_NAME_KEYBOARD,  # add back button
            parse_mode="markdown",
        )

        await States.submit_child_name.set()

    # =============================
    @dp.callback_query_handler(
        cf.filter(action=["teacher_menu"]),
        state=[States.teacher_submit],
    )
    async def submit_teacher_yes_handler(
        call: CallbackQuery, state: FSMContext, callback_data: dict
    ):
        message = call.message
        role = (await state.get_data())["role"]
        logger.info(
            f"{message.chat.id} | {message.chat.username} | {role} | teacher_menu | submit_teacher_yes_button"
        )
        teacher_id = (await state.get_data())["teacher"]
        teacher_name = (await state.get_data())["teacher_name"]
        if (await state.get_data()).get("changed") is None:
            await register_teacher(telegram_id=message.chat.id, teacher_id=teacher_id)

        else:
            await change_role(telegram_id=message.chat.id, teacher_id=teacher_id)

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
        role = (await state.get_data())["role"]
        logger.info(
            f"{message.chat.id} | {message.chat.username} | {role} | administration_menu_first | administration_submit_button"
        )
        school_id = (await state.get_data())["school"]
        school_name = (await state.get_data())["school_name"]
        if (await state.get_data()).get("changed") is None:
            await register_administration(
                telegram_id=message.chat.id, school_id=school_id
            )
        else:
            await change_role(telegram_id=message.chat.id, school_id=school_id)
        await send_message(
            message,
            text=Texts.successful_reg_admin.format(school_name=school_name),
            keyboard=ADMINISTRATION_MENU_FIRST_KEYBOARD,
            parse_mode="markdown",
        )
        await call.answer()
        await States.administration_menu_first.set()
