from typing import List, Tuple

from aiogram.types.inline_keyboard import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.callback_data import CallbackData

from src.api import (
    get_allowed_group,
    get_allowed_letter,
    get_allowed_parallel,
    get_children,
    get_similar_schools,
    get_similar_teachers,
)

cf = CallbackData("callback", "action", "data")


def generate_markup(
    buttons: List[List[Tuple[str, str]]],
) -> InlineKeyboardMarkup:
    """Generate markup from variants.
    Variants must have certain structure. Firsly, variants is a `List` each element of which is a `List` too.
    Variants itself contains `ROW`s for buttons, which are `List`s.
    Every `ROW` contains elements - `Tuple`, identifying button. Number of buttons in row is a number of columns.
    Button is a tuple of `str` - text for button and `CallbackData` for callbacks.
    Valid variants:
    [
        [("1-1", Callback), ("1-2", Callback)],
        [("2-1", Callback)],
        [("3-1", Callback), ("3-2", Callback), ("3-3", Callback)],
    ]

    Args:
        variants (List[List[Tuple(str, str)]]): variants for buttons

    Returns:
        InlineKeyboardMarkup: keyboard markup for message
    """
    keyboard = InlineKeyboardMarkup()  # create instance

    for row in buttons:  # Add row by row
        keyboard.row(
            *[
                InlineKeyboardButton(text=button[0], callback_data=button[1])
                for button in row
            ]
        )

    # Returns result
    return keyboard


STUDENT_MAIN_KEYBOARD = generate_markup(
    [
        [("Следующий урок", cf.new(action="next_lesson", data=0))],
        [
            ("Сегодня", cf.new(action="today", data=0)),
            ("Завтра", cf.new(action="tomorrow", data=0)),
        ],
        [("Определённый день недели", cf.new(action="student_day_of_week", data=0))],
        [("Неделя", cf.new(action="week", data=0))],
        [("Другое меню", cf.new(action="student_misc_menu_first", data=0))],
    ]
)
TEACHER_MAIN_KEYBOARD = generate_markup(
    [
        [("Следующий урок", cf.new(action="next_lesson", data=0))],
        [
            ("Сегодня", cf.new(action="today", data=0)),
            ("Завтра", cf.new(action="tomorrow", data=0)),
        ],
        [("Определённый день недели", cf.new(action="teacher_day_of_week", data=0))],
        [("Неделя", cf.new(action="week", data=0))],
        [("Другое меню", cf.new(action="teacher_misc_menu_first", data=0))],
    ]
)

CHILD_MAIN_KEYBOARD = generate_markup(
    [
        [("Следующий урок", cf.new(action="next_lesson", data=0))],
        [
            ("Сегодня", cf.new(action="today", data=0)),
            ("Завтра", cf.new(action="tomorrow", data=0)),
        ],
        [("Определённый день недели", cf.new(action="child_day_of_week", data=0))],
        [("Неделя", cf.new(action="week", data=0))],
        [("Другое меню", cf.new(action="child_misc_menu_first", data=0))],
        [("Go back", cf.new(action="choose_child", data=0))],
    ]
)

STUDENT_MISC_MENU_FIRST_KEYBOARD = generate_markup(
    [
        [
            ("Найти класс", cf.new(action="find_class", data=0)),
            ("Найти учителя", cf.new(action="find_teacher", data=0)),
        ],
        [("Расписание звонков", cf.new(action="ring_timetable", data=0))],
        [("Написать разработчикам", cf.new(action="contact_devs", data=0))],
        [("Поддержать разработчиков", cf.new(action="support_devs", data=0))],
        [("Вернуться в главное меню", cf.new(action="student_menu", data=0))],
        [("->", cf.new(action="student_misc_menu_second", data=0))],
    ]
)

STUDENT_MISC_MENU_SECOND_KEYBOARD = generate_markup(
    [
        [("Объявления", cf.new(action="anouns", data=0))],
        [("Расписание столовой", cf.new(action="canteen_timetable", data=0))],
        [("Изменить ФИО/класс", cf.new(action="registration", data=0))],
        [("Вернуться в главное меню", cf.new(action="student_menu", data=0))],
        [("<-", cf.new(action="student_misc_menu_first", data=0))],
    ]
)

TEACHER_MISC_MENU_FIRST_KEYBOARD = generate_markup(
    [
        [
            ("Найти класс", cf.new(action="find_class", data=0)),
            ("Найти учителя", cf.new(action="find_teacher", data=0)),
        ],
        [("Расписание звонков", cf.new(action="ring_timetable", data=0))],
        [("Написать разработчикам", cf.new(action="contact_devs", data=0))],
        [("Поддержать разработчиков", cf.new(action="support_devs", data=0))],
        [("Вернуться в главное меню", cf.new(action="teacher_menu", data=0))],
        [("->", cf.new(action="teacher_misc_menu_second", data=0))],
    ]
)

TEACHER_MISC_MENU_SECOND_KEYBOARD = generate_markup(
    [
        [("Объявления", cf.new(action="anouns", data=0))],
        [("Расписание столовой", cf.new(action="canteen_timetable", data=0))],
        [("Изменить ФИО/класс", cf.new(action="registration", data=0))],
        [("Вернуться в главное меню", cf.new(action="teacher_menu", data=0))],
        [("<-", cf.new(action="teacher_misc_menu_first", data=0))],
    ]
)

CHILD_MISC_MENU_FIRST_KEYBOARD = generate_markup(
    [
        [
            ("Найти класс", cf.new(action="find_class", data=0)),
            ("Найти учителя", cf.new(action="find_teacher", data=0)),
        ],
        [("Расписание звонков", cf.new(action="ring_timetable", data=0))],
        [("Расписание Столовой", cf.new(action="canteen_timetable", data=0))],
        [("Вернуться в главное меню", cf.new(action="child_menu", data=0))],
    ]
)
PARENT_MISC_MENU_FIRST_KEYBOARD = generate_markup(
    [
        [("Изменить ФИО/класс", cf.new(action="registration", data=0))],
        [("Вернуться в главное меню", cf.new(action="choose_child", data=0))],
    ]
)


MISC_MENU_SECOND_KEYBOARD = generate_markup(
    [
        [("Объявления", cf.new(action="anouns", data=0))],
        [("Расписание столовой", cf.new(action="canteen_timetable", data=0))],
        [("Изменить ФИО/класс", cf.new(action="registration", data=0))],
        [("Вернуться в главное меню", cf.new(action="main_menu", data=0))],
        [("<-", cf.new(action="misc_menu_first", data=0))],
    ]
)

ADMINISTRATION_MENU_FIRST_KEYBOARD = generate_markup(
    [
        [
            ("Найти класс", cf.new(action="find_class", data=0)),
            ("Найти учителя", cf.new(action="find_teacher", data=0)),
        ],
        [("Расписание звонков", cf.new(action="ring_timetable", data=0))],
        [("Написать разработчикам", cf.new(action="contact_devs", data=0))],
        [("Поддержать разработчиков", cf.new(action="support_devs", data=0))],
        [("->", cf.new(action="administration_menu_second", data=0))],
    ]
)
ADMINISTRATION_MENU_SECOND_KEYBOARD = generate_markup(
    [
        [("Объявления", cf.new(action="anouns", data=0))],
        [("Расписание столовой", cf.new(action="canteen_timetable", data=0))],
        [("Изменить ФИО/класс", cf.new(action="registration", data=0))],
        [("<-", cf.new(action="administration_menu_first", data=0))],
    ]
)

CHILD_DAY_OF_WEEK_KEYBOARD = generate_markup(
    [
        [("Понедельник", cf.new(action="child_choose_day_of_week", data="1"))],
        [("Вторник", cf.new(action="child_choose_day_of_week", data="2"))],
        [("Среда", cf.new(action="child_choose_day_of_week", data="3"))],
        [("Четверг", cf.new(action="child_choose_day_of_week", data="4"))],
        [("Пятница", cf.new(action="child_choose_day_of_week", data="5"))],
        [("Суббота", cf.new(action="child_choose_day_of_week", data="6"))],
        [("go back", cf.new(action="child_menu", data=0))],
    ]
)

STUDENT_DAY_OF_WEEK_KEYBOARD = generate_markup(
    [
        [("Понедельник", cf.new(action="student_choose_day_of_week", data="1"))],
        [("Вторник", cf.new(action="student_choose_day_of_week", data="2"))],
        [("Среда", cf.new(action="student_choose_day_of_week", data="3"))],
        [("Четверг", cf.new(action="student_choose_day_of_week", data="4"))],
        [("Пятница", cf.new(action="student_choose_day_of_week", data="5"))],
        [("Суббота", cf.new(action="student_choose_day_of_week", data="6"))],
        [("go back", cf.new(action="student_menu", data=0))],
    ]
)

TEACHER_DAY_OF_WEEK_KEYBOARD = generate_markup(
    [
        [("Понедельник", cf.new(action="teacher_choose_day_of_week", data="1"))],
        [("Вторник", cf.new(action="teacher_choose_day_of_week", data="2"))],
        [("Среда", cf.new(action="teacher_choose_day_of_week", data="3"))],
        [("Четверг", cf.new(action="teacher_choose_day_of_week", data="4"))],
        [("Пятница", cf.new(action="teacher_choose_day_of_week", data="5"))],
        [("Суббота", cf.new(action="teacher_choose_day_of_week", data="6"))],
        [("go back", cf.new(action="teacher_menu", data=0))],
    ]
)


async def get_child_keyboard(name: int):  # TODO add api
    children = await get_children(name)
    keyboard = [
        [(child_name, cf.new(action="child_menu", data=child_id))]
        for child_name, child_id in children.items()
    ]

    keyboard += [[("parent menu #1", cf.new(action="parent_misc_menu_first", data=0))]]
    return generate_markup(keyboard)


async def get_find_enter_parallel_keyboard(user_id):
    allowed_parallel = await get_allowed_parallel(user_id=user_id)
    return generate_markup(
        [
            [(f"{i}", cf.new(action="find_enter_letter", data=i))]
            for i in allowed_parallel
        ]
    )


async def get_find_enter_letter_keyboard(user_id, current_chosen):
    allowed_letter = await get_allowed_letter(
        user_id=user_id, current_chosen=current_chosen
    )
    return generate_markup(
        [[(f"{i}", cf.new(action="find_enter_group", data=i))] for i in allowed_letter]
    )


async def get_find_enter_group_keyboard(user_id, current_chosen):
    allowed_group = await get_allowed_group(
        user_id=user_id, current_chosen=current_chosen
    )
    return generate_markup(
        [
            [(f"{i}", cf.new(action="find_student_submit", data=i))]
            for i in allowed_group
        ]
    )


async def get_enter_parallel_keyboard():
    return generate_markup(
        [[(f"{i}", cf.new(action="enter_letter", data=i))] for i in range(8, 11 + 1)]
    )


async def get_enter_letter_keyboard():
    return generate_markup(
        [[(f"{i}", cf.new(action="enter_group", data=i))] for i in "ABCDEF"]
    )


async def get_enter_group_keyboard():
    return generate_markup(
        [[(f"{i}", cf.new(action="student_submit", data=i))] for i in range(1, 2 + 1)]
    )


STUDENT_SUBMIT_KEYBOARD = generate_markup(
    [
        [(f"YES", cf.new(action="student_submit_yes", data=0))],
        [(f"NO", cf.new(action="enter_parallel", data=0))],
    ]
)

FIND_STUDENT_SUBMIT_KEYBOARD = generate_markup(
    [
        [(f"YES", cf.new(action="find_menu", data=0))],
        [(f"NO", cf.new(action="find_class", data=0))],
    ]
)

FIND_TEACHER_SUBMIT_KEYBOARD = generate_markup(
    [
        [(f"YES", cf.new(action="find_menu", data=0))],
        [(f"NO", cf.new(action="find_teacher", data=0))],
    ]
)

FIND_MAIN_KEYBOARD = generate_markup(
    [
        [("Следующий урок", cf.new(action="next_lesson", data=0))],
        [
            ("Сегодня", cf.new(action="today", data=0)),
            ("Завтра", cf.new(action="tomorrow", data=0)),
        ],
        [("Определённый день недели", cf.new(action="find_day_of_week", data=0))],
        [("Неделя", cf.new(action="week", data=0))],
    ]
)

FIND_DAY_OF_WEEK_KEYBOARD = generate_markup(
    [
        [("Понедельник", cf.new(action="find_choose_day_of_week", data="1"))],
        [("Вторник", cf.new(action="find_choose_day_of_week", data="2"))],
        [("Среда", cf.new(action="find_choose_day_of_week", data="3"))],
        [("Четверг", cf.new(action="find_choose_day_of_week", data="4"))],
        [("Пятница", cf.new(action="find_choose_day_of_week", data="5"))],
        [("Суббота", cf.new(action="find_choose_day_of_week", data="6"))],
        [("go back", cf.new(action="find_menu", data=0))],
    ]
)


async def find_get_teachers_keyboard(teacher):
    teachers = await get_similar_teachers(teacher)
    return generate_markup(
        [
            [
                (
                    teacher["name"],
                    cf.new(action="find_choose_teacher", data=teacher["id"]),
                )
            ]
            for teacher in teachers
        ]
    )


async def get_teachers_keyboard(teacher):
    teachers = await get_similar_teachers(teacher)
    return generate_markup(
        [[(name, cf.new(action="choose_teacher", data=name))] for name in teachers]
    )


CHOOSE_ROLE_KEYBOARD = generate_markup(
    [
        [("Parent", cf.new(action="show_childs", data=0))],
        [("Student", cf.new(action="input_school", data="Student"))],
        [("Teacher", cf.new(action="input_school", data="Teacher"))],
        [("Administration", cf.new(action="input_school", data="Administration"))],
    ]
)


async def get_schools_keyboard(school: str):
    schools = await get_similar_schools(school)
    keyboard = [
        [(school["name"], cf.new(action="choose_school", data=school["id"]))]
        for school in schools
    ]

    return generate_markup(keyboard)


SUBMIT_ADMINISTRATION_KEYBOARD = generate_markup(
    [
        [("Yes", cf.new(action="administration_menu_first", data=0))],
        [("No", cf.new(action="choose_role", data=0))],
    ]
)

TEACHER_SUBMIT_KEYBOARD = generate_markup(
    [
        [("Yes", cf.new(action="teacher_menu", data=0))],
        [("No", cf.new(action="input_school", data=0))],
    ]
)

ADD_MORE_CHILDREN_KEYBOARD = generate_markup(
    [
        [("Yes", cf.new(action="input_school", data=0))],
        [("No", cf.new(action="choose_child", data=0))],
    ]
)
