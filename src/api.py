import asyncio
from typing import Union
from src.logger import logger
from src.redis import *  # TODO remove star import
from datetime import datetime
import aiohttp
import ujson

url = "http://172.0.0.7:8009"


def get_current_day_of_week():
    return datetime.today().weekday() + 1


async def get_request(request: str, data):  # TODO 200 status code handler
    logger.debug(f"get_request to {url}/api{request} with data: {data}")
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{url}/api{request}", json=data) as response:
            response = await response.read()
            answer = ujson.loads(response)
            logger.debug(f"answer to request: {answer}")
            return answer


async def post_request(request: str, data):  # TODO 200 status code handler
    logger.debug(f"get_request to {url}/api{request} with data: {data}")
    async with aiohttp.ClientSession() as session:
        async with session.post(f"{url}/api{request}", json=data) as response:
            response = await response.read()
            return ujson.loads(response)


async def put_request(request: str, data):  # TODO 200 status code handler
    logger.debug(f"get_request to {url}/api{request} with data: {data}")
    async with aiohttp.ClientSession() as session:
        async with session.put(f"{url}/api{request}", json=data) as response:
            response = await response.read()
            return ujson.loads(response)


# ~=============================


async def get_user_next_lesson(
    telegram_id, is_searching=False, teacher_id=None, subclass_id=None
):
    """
    Returns timetable for user with `telegram_id` if `is_searching` == False
    Else return timetable for `teacher_id` or `subclass_id` (Only one must be set)
    """
    school_id = await get_school_id(telegram_id)
    # TODO: understand next lesson number and day of week
    lesson_number = 1
    day_of_week = 1

    if is_searching:
        if teacher_id is not None:
            data = {"teacher_id": teacher_id}
        else:
            data = {"subclass_id": subclass_id}
    else:
        main_role = await get_main_role(telegram_id)
        if main_role == "teacher":
            data = {"teacher_id": get_teacher_id(telegram_id)}
        else:
            data = {"subclass_id": get_subclass_id(teacher_id)}
    data = await get_request(
        "/lesson/get/certain",
        data={
            "data": data,
            "school_id": school_id,
            "day_of_week": day_of_week,
            "lesson_number": lesson_number,
        },
    )
    return data


async def get_user_today(
    telegram_id, is_searching=False, teacher_id=None, subclass_id=None
):
    """
    Returns timetable for user with `telegram_id` if `is_searching` == False
    Else return timetable for `teacher_id` or `subclass_id` (Only one must be set)
    """
    day_of_week = get_current_day_of_week()
    school_id = await get_school_id(telegram_id)

    if is_searching:
        if teacher_id is not None:
            data = {"teacher_id": teacher_id}
        else:
            data = {"subclass_id": subclass_id}
    else:
        main_role = await get_main_role(telegram_id)

        if main_role == "teacher":
            data = {"teacher_id": get_teacher_id(telegram_id)}
        else:
            data = {"subclass_id": get_subclass_id(telegram_id)}

    data = await get_request(
        "/lesson/get/day",
        data={"data": data, "school_id": school_id, "day_of_week": day_of_week},
    )

    return data


async def get_user_tomorrow(
    telegram_id, is_searching=False, teacher_id=None, subclass_id=None
):
    """
    Returns timetable for user with `telegram_id` if `is_searching` == False
    Else return timetable for `teacher_id` or `subclass_id` (Only one must be set)
    """
    day_of_week = get_current_day_of_week()
    day_of_week = day_of_week % 7 + 1
    school_id = await get_school_id(telegram_id)

    if is_searching:
        if teacher_id is not None:
            data = {"teacher_id": teacher_id}
        else:
            data = {"subclass_id": subclass_id}
    else:
        main_role = await get_main_role(telegram_id)

        if main_role == "teacher":
            data = {"teacher_id", get_teacher_id(telegram_id)}
        else:
            data = {"subclass_id", get_subclass_id(telegram_id)}

    data = await get_request(
        "/lesson/get/day",
        data={"data": data, "school_id": school_id, "day_of_week": day_of_week},
    )
    return data


async def get_user_week(
    telegram_id, is_searching=False, teacher_id=None, subclass_id=None
):
    """
    Returns timetable for user with `telegram_id` if `is_searching` == False
    Else return timetable for `teacher_id` or `subclass_id` (Only one must be set)
    """
    school_id = get_school_id(telegram_id)
    if is_searching:
        if teacher_id is not None:
            data = {"teacher_id": teacher_id}
        else:
            data = {"subclass_id": subclass_id}
    else:
        main_role = await get_main_role(telegram_id)

        if main_role == "teacher":
            data = {"teacher_id", get_teacher_id(telegram_id)}
        else:
            data = {"subclass_id", get_subclass_id(telegram_id)}

    data = await get_request(
        "/lesson/get/range",
        data={
            "data": data,
            "start_index": 1,
            "end_index": 1,
            "school_id": school_id,
        },
    )
    return data


async def get_user_day_of_week(
    telegram_id, day_of_week, is_searching=False, teacher_id=None, subclass_id=None
):
    """
    Returns timetable for user with `telegram_id` if `is_searching` == False
    Else return timetable for `teacher_id` or `subclass_id` (Only one must be set)
    """
    school_id = await get_school_id(telegram_id)
    if is_searching:
        if teacher_id is not None:
            data = {"teaher_id": teacher_id}
        else:
            data = {"subclass_id": subclass_id}
    else:
        main_role = get_main_role(telegram_id)

        if main_role == "teacher":
            data = {"teacher_id", get_teacher_id(telegram_id)}
        else:
            data = {"subclass_id", get_subclass_id(telegram_id)}
    data = await get_request(
        "/lesson/get/day",
        data={"data": data, "school_id": school_id, "day_of_week": day_of_week},
    )
    return data


# ~=============================


async def get_ring_timetable(telegram_id: int):
    school_id = await get_school_id(telegram_id)
    data = await get_request("/info/lessontimetable/all", data={"school_id": school_id})
    return data


async def get_canteen_timetable(telegram_id: int):
    school_id = await get_school_id(telegram_id)
    corpuses = await get_request(
        "/api/info/corpuses/all", data={"school_id": school_id}
    )
    corpuses = list(map(lambda c: (c["name"], c["id"]), corpuses["data"]))

    canteen_texts = {}
    for corpus_name, corpus_id in corpuses:
        canteen_text = await get_request(
            "/api/info/corpus/canteen", data={"corpus_id": corpus_id}
        )
        canteen_texts[corpus_name] = canteen_text["data"]

    return canteen_texts


# ~=============================


async def get_allowed_parallel(is_searching, telegram_id=None, school_id=None):
    """
    If `is_searching` is True, returns for `school_id` for account `telegram_id`.
    Else returns for school with `school_id`
    Only one of `telegram_id` and `school_id` must be set
    """
    if is_searching:
        school_id = await get_school_id(telegram_id)
    data = await get_request("/info/parallels/all", data={"school_id": school_id})
    return data


async def get_allowed_letter(is_searching, parallel, telegram_id=None, school_id=None):
    """
    If `is_searching` is True, returns for `school_id` for account `telegram_id`.
    Else returns for school with `school_id`
    Only one of `telegram_id` and `school_id` must be set
    """
    if is_searching:
        school_id = await get_school_id(telegram_id)

    data = await get_request(
        "/info/letters/all",
        data={"school_id": school_id, "educational_level": parallel},
    )
    return data


async def get_allowed_group(
    is_searching, parallel, letter, telegram_id=None, school_id=None
):
    """
    If `is_searching` is True, returns for `school_id` for account `telegram_id`.
    Else returns for school with `school_id`
    Only one of `telegram_id` and `school_id` must be set
    """
    if is_searching:
        school_id = get_school_id(telegram_id)

    data = await get_request(
        "/info/groups/all",
        data={
            "school_id": school_id,
            "educational_level": parallel,
            "identificator": letter,
        },
    )
    return data


async def is_registered(telegram_id):
    logger.debug(f"request is_registered for {telegram_id}")
    data = await get_request("/info/check/telegramid", {"telegram_id": telegram_id})
    return data["data"]


async def get_similar_schools(school):
    # data = await get_request("/info/schools/distance", {"name": school})
    data = {"data": [{"id": 2147483647, "name": "1580"}]}
    logger.debug(f"get_similar_schools for {school}; answer: {data}")
    return data["data"]


async def get_similar_teachers(teacher_name, school_id):
    data = await get_request(
        "/info/teachers/distance", {"name": teacher_name, "school_id": school_id}
    )
    return data


# ~=============================
async def register_student(telegram_id, subclass_id):
    data = await post_request(
        "/registration/student",
        {"telegram_id": telegram_id, "subclass_id": subclass_id},
    )
    await save_to_redis(data)


async def register_child(telegram_id, subclass_id):
    data = await post_request(
        "/rolemanagement/add/child",
        {"parent_id": telegram_id, "subclass_id": subclass_id},
    )
    await save_to_redis(data)


async def register_teacher(telegram_id, teacher_id):
    data = await post_request(
        "/registration/teacher", {"telegram_id": telegram_id, "teacher_id": teacher_id}
    )
    await save_to_redis(data)


async def register_administration(telegram_id, school_id):
    data = await post_request(
        "/registration/administration",
        {"telegram_id": telegram_id, "school_id": school_id},
    )
    await save_to_redis(data)


# ~=============================


async def get_user_roles(telegram_id):
    """
    Returns all user roles by telegram_id
    """
    data = await post_request("/rolemanagement/get", {"telegram_id": telegram_id})
    await save_to_redis(data)
