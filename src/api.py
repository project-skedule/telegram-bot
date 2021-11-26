import asyncio
from typing import Union
from src.logger import logger

import aiohttp
import ujson

url = "http://0.0.0.1:8009"


async def get_request(request: str, data):  # TODO 200 status code handler
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{url}/api{request}", json=data) as response:
            response = await response.read()
            return ujson.loads(response)


async def post_request(request: str, data):  # TODO 200 status code handler
    async with aiohttp.ClientSession() as session:
        async with session.post(f"{url}/api{request}", json=data) as response:
            response = await response.read()
            return ujson.loads(response)


async def put_request(request: str, data):  # TODO 200 status code handler
    async with aiohttp.ClientSession() as session:
        async with session.put(f"{url}/api{request}", json=data) as response:
            response = await response.read()
            return ujson.loads(response)


# ~=============================


async def get_school(user_id):  # TODO add redis
    return "1580"


async def get_teacher_name(user_id):  # TODO add redis
    return "Иванов К. Ю."


async def get_student_class(user_id):  # TODO add redis
    return "11Е1"


# ~=============================
async def get_teacher_next_lesson(user_id=None, teacher_name=None):
    if user_id is not None:
        teacher_name = await get_teacher_name(user_id)
    return f"next lesson for {teacher_name}"


async def get_teacher_today(user_id=None, teacher_name=None):
    if user_id is not None:
        teacher_name = await get_teacher_name(user_id)
    return f"today for {teacher_name}"


async def get_teacher_tomorrow(user_id=None, teacher_name=None):
    if user_id is not None:
        teacher_name = await get_teacher_name(user_id)
    return f"tomorrow for {teacher_name}"


async def get_teacher_week(user_id=None, teacher_name=None):
    if user_id is not None:
        teacher_name = await get_teacher_name(user_id)
    return f"week for {teacher_name}"


async def get_teacher_day_of_week(user_id=None, teacher_name=None, day=None):
    if user_id is not None:
        teacher_name = await get_teacher_name(user_id)
    return f"day of week #{day} for {teacher_name}"


# ~=============================


async def get_student_next_lesson(user_id=None, class_name=None):
    if user_id is not None:
        class_name = await get_student_class(user_id)
    return f"next lesson for {class_name}"


async def get_student_today(user_id=None, class_name=None):
    if user_id is not None:
        class_name = await get_student_class(user_id)
    return f"today for {class_name}"


async def get_student_tomorrow(user_id=None, class_name=None):
    if user_id is not None:
        class_name = await get_student_class(user_id)
    return f"tomorrow for {class_name}"


async def get_student_week(user_id=None, class_name=None):
    if user_id is not None:
        class_name = await get_student_class(user_id)
    return f"week for {class_name}"


async def get_student_day_of_week(user_id=None, class_name=None, day=None):
    if user_id is not None:
        class_name = await get_student_class(user_id)
    return f"day of week #{day} for {class_name}"


# ~=============================


async def get_ring_timetable(name: int):
    return f"*РАСПИСАНИЕ ЗВОНКОВ* for {name}:\nНОМЕР    ВРЕМЯ                ПЕРЕМЕНА\n0 урок      08:15 - 08:55      5\n1 урок      09:00 - 09:40      10\n2 урок      09:50 - 10:30      15\n3 урок      10:45 - 11:25      15\n4 урок      11:40 - 12:20      20\n5 урок      12:40 - 13:20      20\n6 урок      13:40 - 14:20      20\n7 урок      14:40 - 15:20      10\n8 урок      15:30 - 16:10"


async def get_canteen_timetable(name: int):
    return f"*1 КОРПУС:*\n\n*БУФЕТ* for {name}:\nПонедельник-пятница - 9:00 - 15:00\nСуббота - 10:00 - 14:00\n\nСТОЛОВАЯ:\n\n*РАСПИСАНИЕ ЗАВТРАКОВ:*\n10ые классы - 9:40 - 9:50\n11ые классы - 10:30 - 10:45\n\n*РАСПИСАНИЕ ОБЕДОВ:*\n10ые классы - 12:20 - 12:40\n11ые классы - 13:20 - 13:40\n\n\n*2 КОРПУС:*\n\n*СТОЛОВАЯ:*\n\n*РАСПИСАНИЕ ЗАВТРАКОВ:*\n8ые классы - 9:40 - 9:50\n9ые классы - 10:30 - 10:45\n10-11ые классы - 11:25 - 11:40\n\n*РАСПИСАНИЕ ОБЕДОВ:*\n8ые классы - 12:20 - 12:40\n9ые классы - 13:20 - 13:40\n10-11ые классы - 14:20 - 14:40"


# ~=============================


async def get_children(name: int):
    return {"child 1": "id1", "child 2": "id2"}


# ~=============================
async def get_allowed_parallel(user_id=None, school=None):
    if user_id is not None:
        school = await get_school(user_id)
    return [8, 9, 10, 11]


async def get_allowed_letter(user_id=None, school=None, current_chosen=None):
    if user_id is not None:
        school = await get_school(user_id)
    return list("abcd")


async def get_allowed_group(
    user_id=None, school=None, current_chosen=None
):  # TODO split class
    if user_id is not None:
        school = await get_school(user_id)
    return list("12")


async def is_registered(user_id):
    return False
    response = await get_request("/info/check/telegramid", {"telegram_id": user_id})
    logger.debug(response)
    return response["data"]


async def get_similar_schools(school):
    response = await get_request("/info/schools/distance", {"name": school})
    return response["data"]


async def get_similar_teachers(teacher):  # TODO add school
    school_id = 1  # TODO: GET AS PARAMETER
    response = await get_request(
        "/info/teachers/distance", {"name": teacher, "school_id": school_id}
    )
    return response["data"]


# ~=============================
async def register_student(user_id, school, class_name):
    subclass_id = 1  # TODO: GET AS PARAMETER
    response = await post_request(
        "/registration/student", {"telegram_id": user_id, "subclass_id": subclass_id}
    )
    logger.debug(
        f"register student with id: {user_id} school: {school} class: {class_name}"
    )
    # TODO: update redis


async def register_child(user_id, school, class_name):
    subclass_id = 1  # TODO: GET AS PARAMETER
    response = await post_request(
        "/rolemanagement/add/child", {"parent_id": user_id, "subclass_id": subclass_id}
    )
    logger.debug(
        f"register child for id: {user_id} school: {school} class: {class_name}"
    )
    # TODO: update reddis


async def register_teacher(user_id, teacher_id):
    response = await post_request(
        "/registration/teacher", {"telegram_id": user_id, "teacher_id": teacher_id}
    )
    logger.debug(f"register teacher for id: {user_id} teacher: {teacher_id}")
    # TODO: update reddis


async def register_administration(user_id, school):
    school_id = 1  # TODO: GET AS PARAMETER
    response = await post_request(
        "/registration/administration", {"telegram_id": user_id, "school_id": school_id}
    )
    logger.debug(f"register administration for id: {user_id} school: {school}")
    # TODO: update reddis


# ~=============================


async def get_user_roles(user_id):
    # TODO: get from reddis
    response = await post_request("/rolemanagement/get", {"telegram_id": user_id})
    logger.debug(f"get user roles for {user_id}")
    return {}
    # TODO: update reddis
