from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, Message
from ..text_loader import Texts

from ..api import (
    get_student_day_of_week,
    get_student_next_lesson,
    get_student_today,
    get_student_tomorrow,
    get_student_week,
    get_teacher_day_of_week,
    get_teacher_next_lesson,
    get_teacher_today,
    get_teacher_tomorrow,
    get_teacher_week,
)

from ..bot import bot, dp
from ..keyboards import (
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
from ..logger import logger
from ..some_functions import dispatcher_menu, is_find_for_student, send_message
from ..states import States


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
        await state.update_data({"class": ""})
        await state.update_data({"teacher": None})
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
        await state.update_data({"class": f"{callback_data['data']}"})
        message = call.message
        await send_message(
            message,
            Texts.enter_letter,
            await get_find_enter_letter_keyboard(
                message.chat.id, (await state.get_data())["class"]
            ),
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
        await state.update_data(
            {"class": f"{(await state.get_data())['class']}{callback_data['data']}"}
        )
        message = call.message
        await send_message(
            message,
            Texts.enter_group,
            await get_find_enter_group_keyboard(
                message.chat.id, (await state.get_data())["class"]
            ),
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
        await States.find_student_submit.set()
        await state.update_data(
            {"class": f"{(await state.get_data())['class']}{callback_data['data']}"}
        )
        message = call.message
        await send_message(
            message,
            Texts.confirm_class(subclass=(await state.get_data())["class"]),
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
            text = f"поиск ученика: `{(await state.get_data())['class']}`"
        else:
            text = f"поиск учителя: `{(await state.get_data())['teacher']}`"
        await send_message(
            message,
            text,
            FIND_MAIN_KEYBOARD,
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
    async def find_day_of_week_handler(
        call: CallbackQuery, state: FSMContext, callback_data: dict
    ):
        message = call.message
        role = (await state.get_data())["role"]
        day_of_week = callback_data["data"]
        if await is_find_for_student(state):
            text = await get_student_day_of_week(
                class_name=(await state.get_data()["class"]), day=day_of_week
            )
        else:
            text = await get_teacher_day_of_week(
                class_name=(await state.get_data()["teacher"]), day=day_of_week
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
            text = await get_student_next_lesson(
                class_name=(await state.get_data())["class"]
            )
        else:
            text = await get_teacher_next_lesson(
                class_name=(await state.get_data())["teacher"]
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
        message = call.message
        role = (await state.get_data())["role"]
        if await is_find_for_student(state):
            text = await get_student_today(class_name=(await state.get_data())["class"])
        else:
            text = await get_teacher_today(
                class_name=(await state.get_data())["teacher"]
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
            text = await get_student_tomorrow(
                class_name=(await state.get_data())["class"]
            )
        else:
            text = await get_teacher_tomorrow(
                class_name=(await state.get_data())["teacher"]
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
        if await is_find_for_student(state):
            text = await get_student_week(class_name=(await state.get_data())["class"])
        else:
            text = await get_teacher_week(
                class_name=(await state.get_data())["teacher"]
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
    async def find_input_teacher_handler(
        call: CallbackQuery, state: FSMContext, callback_data: dict
    ):
        await States.find_input_teacher.set()
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
                (await state.get_data())["teacher"]
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
        text = f"sure? {callback_data['data']}"
        await state.update_data({"teacher": callback_data["data"]})
        await send_message(
            message,
            text=text,
            keyboard=FIND_TEACHER_SUBMIT_KEYBOARD,
            parse_mode="markdown",
        )
        await call.answer()
