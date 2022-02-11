import asyncio
from typing import Union
from src.logger import logger
from src.redis import *  # TODO remove star import
from datetime import datetime
import aiohttp
import ujson
from aiogram.utils import markdown
from src.texts import Texts

from src.constants import DAYS_OF_WEEK

url = "http://172.0.0.7:8009"


def get_current_day_of_week():
    return datetime.today().weekday() + 1


async def get_request(request: str, data=None):  # TODO 200 status code handler
    logger.debug(f"get_request to {url}/api{request} with data: {data}")
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{url}/api{request}", json=data) as response:
            response = await response.read()
            logger.debug(f"answer to request: {response}")
            return ujson.loads(response)


async def post_request(request: str, data=None):  # TODO 200 status code handler
    logger.debug(f"post_request to {url}/api{request} with data: {data}")
    async with aiohttp.ClientSession() as session:
        async with session.post(f"{url}/api{request}", json=data) as response:
            response = await response.read()
            logger.debug(f"answer to request: {response}")
            return ujson.loads(response)


async def put_request(request: str, data=None):  # TODO 200 status code handler
    logger.debug(f"put_request to {url}/api{request} with data: {data}")
    async with aiohttp.ClientSession() as session:
        async with session.put(f"{url}/api{request}", json=data) as response:
            response = await response.read()
            logger.debug(f"answer to request: {response}")
            return ujson.loads(response)


# ~=============================


async def get_user_today(
    telegram_id, is_searching=False, teacher_id=None, subclass_id=None
):
    return await get_user_day_of_week(
        telegram_id,
        get_current_day_of_week(),
        is_searching=is_searching,
        teacher_id=teacher_id,
        subclass_id=subclass_id,
    )


async def get_user_tomorrow(
    telegram_id, is_searching=False, teacher_id=None, subclass_id=None
):
    return await get_user_day_of_week(
        telegram_id,
        get_current_day_of_week() % 7 + 1,
        is_searching=is_searching,
        teacher_id=teacher_id,
        subclass_id=subclass_id,
    )


async def get_student_day_of_week(
    telegram_id, day_of_week, subclass_id, subclass_name=None
):
    school_id = await get_school_id(telegram_id)

    data = {"subclass_id": subclass_id}

    data = await get_request(
        "/lesson/get/day",
        data={"data": data, "school_id": school_id, "day_of_week": day_of_week},
    )

    lessons = data["lessons"]

    result = ""

    for lesson in lessons:
        number = lesson["lesson_number"]
        result += markdown.underline(
            f"Урок №{number['number']} {number['time_start']} - {number['time_end']}\n"
        )
        subject = markdown.escape_md(lesson["subject"])
        teacher = markdown.escape_md(lesson["teacher"]["name"])
        corpus = markdown.escape_md(lesson["cabinet"]["corpus"]["name"])
        cabinet = markdown.escape_md(lesson["cabinet"]["name"])

        result += f"Предмет: *{subject}*\n"
        result += f"{teacher}\n"
        result += f"{corpus}, {cabinet}\n"
        result += "\n"

    day_of_week = DAYS_OF_WEEK[day_of_week]
    if result.strip() == "":
        if subclass_name is not None:
            return f"У класса {subclass_name} нет уроков *{day_of_week}*\n"
        else:
            return f"У вас нет уроков *{day_of_week}*\n"
    else:
        if subclass_name is not None:
            return f"Расписание класса {subclass_name} *{day_of_week}*:\n" + result
        else:
            return f"Ваше расписание *{day_of_week}*:\n" + result


async def get_teacher_day_of_week(
    telegram_id, day_of_week, teacher_id, teacher_name=None
):
    school_id = await get_school_id(telegram_id)

    data = {"teacher_id": teacher_id}

    data = await get_request(
        "/lesson/get/day",
        data={"data": data, "school_id": school_id, "day_of_week": day_of_week},
    )

    lessons = data["lessons"]

    result = ""
    for lesson in lessons:
        number = lesson["lesson_number"]
        result += markdown.underline(
            f"Урок №{number['number']} {number['time_start']} - {number['time_end']}\n"
        )

        subject = markdown.escape_md(lesson["subject"])
        result += f"Предмет: {subject}\n"
        subclasses = lesson["subclasses"]
        for subclass in subclasses:
            name = f"*{subclass['educational_level']}{subclass['identificator']}{subclass['additional_identificator']}*, "
            result += name
        result = result[:-2] + "\n"

        corpus = markdown.escape_md(lesson["cabinet"]["corpus"]["name"])
        cabinet = markdown.escape_md(lesson["cabinet"]["name"])

        result += f"{corpus}, {cabinet}\n"
        result += "\n"

    day_of_week = DAYS_OF_WEEK[day_of_week]
    if result.strip() == "":
        if teacher_name is not None:
            return f"У учителя {markdown.escape_md(teacher_name)} нет уроков *{day_of_week}*\n"
        else:
            return f"У вас нет уроков *{day_of_week}*\n"
    else:
        if teacher_name is not None:
            return (
                f"Расписание учителя {markdown.escape_md(teacher_name)} *{day_of_week}*:\n"
                + result
            )
        else:
            return f"Ваше расписание *{day_of_week}*:\n" + result


async def get_user_day_of_week(
    telegram_id, day_of_week, is_searching=False, teacher_id=None, subclass_id=None
):
    """
    Returns timetable for user with `telegram_id` if `is_searching` == False
    Else return timetable for `teacher_id` or `subclass_id` (Only one must be set)
    """
    if is_searching:
        if teacher_id is not None:
            teacher_name = await get_teacher_name_by_id(teacher_id)
            return await get_teacher_day_of_week(
                telegram_id, day_of_week, teacher_id, teacher_name
            )
        else:
            subclass_name = await get_subclass_name_by_id(subclass_id)
            return await get_student_day_of_week(
                telegram_id, day_of_week, subclass_id, subclass_name
            )
    else:
        main_role = await get_main_role(telegram_id)

        if main_role == "Teacher":
            return await get_teacher_day_of_week(
                telegram_id, day_of_week, await get_teacher_id(telegram_id)
            )
        else:
            return await get_student_day_of_week(
                telegram_id, day_of_week, await get_subclass_id(telegram_id)
            )


async def get_student_week(telegram_id, student_id, subclass_name=None):
    school_id = await get_school_id(telegram_id)

    data = {"subclass_id": student_id}

    data = await get_request(
        "/lesson/get/range",
        data={
            "data": data,
            "start_index": 1,
            "end_index": 7,
            "school_id": school_id,
        },
    )

    result = ""
    days_of_week = data["data"]
    for day in days_of_week:
        lessons = day["lessons"]
        day_of_week = day["day_of_week"]

        name_day = DAYS_OF_WEEK[day_of_week]
        if subclass_name is not None:
            result += markdown.underline(
                f"Расписание класса {subclass_name} {name_day}:\n"
            )
        else:
            result += markdown.underline(f"Ваше расписание {name_day}:\n")

        for lesson in lessons:
            number = lesson["lesson_number"]
            result += markdown.italic(
                f"Урок №{number['number']} {number['time_start']} - {number['time_end']}\n"
            )

            subject = markdown.escape_md(lesson["subject"])
            teacher = markdown.escape_md(lesson["teacher"]["name"])
            corpus = markdown.escape_md(lesson["cabinet"]["corpus"]["name"])
            cabinet = markdown.escape_md(lesson["cabinet"]["name"])

            result += f"Предмет: *{subject}*\n"
            result += f"{teacher}\n"
            result += f"{corpus}, {cabinet}\n"
            result += "\n"
        result += "\n"

    return result


async def get_teacher_week(telegram_id, teacher_id, teacher_name=None):
    school_id = await get_school_id(telegram_id)

    data = {"teacher_id": teacher_id}

    data = await get_request(
        "/lesson/get/range",
        data={
            "data": data,
            "start_index": 1,
            "end_index": 7,
            "school_id": school_id,
        },
    )

    result = ""
    days_of_week = data["data"]
    for day in days_of_week:
        lessons = day["lessons"]
        day_of_week = day["day_of_week"]
        name_day = DAYS_OF_WEEK[day_of_week]
        if teacher_name is not None:
            result += markdown.underline(
                f"Расписание учителя {markdown.escape_md(teacher_name)} {name_day}:\n"
            )
        else:
            result += markdown.underline(f"Ваше расписание {name_day}:\n")

        for lesson in lessons:
            number = lesson["lesson_number"]
            result += markdown.escape_md(
                f"Урок №{number['number']} {number['time_start']} - {number['time_end']}\n"
            )

            subject = markdown.escape_md(lesson["subject"])
            result += f"Предмет: {subject}\n"
            subclasses = lesson["subclasses"]

            for subclass in subclasses:
                name = f"*{subclass['educational_level']}{subclass['identificator']}{subclass['additional_identificator']}*, "
                result += name
            result = result[:-2] + "\n"

            corpus = markdown.escape_md(lesson["cabinet"]["corpus"]["name"])
            cabinet = markdown.escape_md(lesson["cabinet"]["name"])

            result += f"{corpus}, {cabinet}\n"
            result += "\n"
        result += "\n"

    return result


async def get_user_week(
    telegram_id, is_searching=False, teacher_id=None, subclass_id=None
):
    """
    Returns timetable for user with `telegram_id` if `is_searching` == False
    Else return timetable for `teacher_id` or `subclass_id` (Only one must be set)
    """
    school_id = await get_school_id(telegram_id)
    if is_searching:
        if teacher_id is not None:
            teacher_name = await get_teacher_name_by_id(teacher_id)
            return await get_teacher_week(telegram_id, teacher_id, teacher_name)
        else:
            subclass_name = await get_subclass_name_by_id(subclass_id)
            return await get_student_week(telegram_id, subclass_id, subclass_name)
    else:
        main_role = await get_main_role(telegram_id)

        if main_role == "Teacher":
            return await get_teacher_week(
                telegram_id, await get_teacher_id(telegram_id)
            )
        else:
            return await get_student_week(
                telegram_id, await get_subclass_id(telegram_id)
            )


# ~=============================


async def get_ring_timetable(telegram_id: int):
    school_id = await get_school_id(telegram_id)
    data = await get_request(
        "/info/lessontimetables/all", data={"school_id": school_id}
    )
    return data["data"]


async def get_canteen_timetable(telegram_id: int):
    school_id = await get_school_id(telegram_id)
    corpuses = await get_request("/info/corpuses/all", data={"school_id": school_id})
    corpuses = list(map(lambda c: (c["name"], c["id"]), corpuses["data"]))

    canteen_texts = {}
    for corpus_name, corpus_id in corpuses:
        canteen_text = await get_request(
            "/info/corpus/canteen", data={"corpus_id": corpus_id}
        )
        canteen_texts[corpus_name] = canteen_text["data"]

    return canteen_texts


# ~=============================


async def get_allowed_parallel(telegram_id=None):
    """
    If `is_searching` is True, returns for `school_id` for account `telegram_id`.
    Else returns for school with `school_id`
    Only one of `telegram_id` and `school_id` must be set
    """
    school_id = await get_school_id(telegram_id)
    data = await get_request("/info/parallels/all", data={"school_id": school_id})
    return data["data"]


async def get_allowed_letter(parallel, telegram_id=None):
    """
    If `is_searching` is True, returns for `school_id` for account `telegram_id`.
    Else returns for school with `school_id`
    Only one of `telegram_id` and `school_id` must be set
    """

    school_id = await get_school_id(telegram_id)

    data = await get_request(
        "/info/letters/all",
        data={"school_id": school_id, "educational_level": parallel},
    )
    return data["data"]


async def get_allowed_group(parallel, letter, telegram_id=None):
    """
    If `is_searching` is True, returns for `school_id` for account `telegram_id`.
    Else returns for school with `school_id`
    Only one of `telegram_id` and `school_id` must be set
    """

    school_id = await get_school_id(telegram_id)

    data = await get_request(
        "/info/groups/all",
        data={
            "school_id": school_id,
            "educational_level": parallel,
            "identificator": letter,
        },
    )
    return data["data"]


async def is_registered(telegram_id):
    logger.debug(f"request is_registered for {telegram_id}")
    data = await get_request("/info/check/telegramid", {"telegram_id": telegram_id})
    return data["data"]


async def get_similar_schools(school):
    data = await get_request("/info/schools/distance", {"name": school})
    # data = {"data": [{"id": 2147483647, "name": "1580"}]}
    logger.debug(f"get_similar_schools for {school}; answer: {data}")
    return data["data"]


async def get_similar_teachers(teacher_name, school_id):
    data = await get_request(
        "/info/teachers/distance", {"name": teacher_name, "school_id": school_id}
    )
    return data["data"]


async def get_current_lesson(school_id):
    data = await get_request("/info/lessontimetables/all", {"school_id": school_id})
    for lesson in data["data"]:
        start = datetime.strptime(lesson["time_start"], "%H:%M").time()
        end = datetime.strptime(lesson["time_end"], "%H:%M").time()
        now = datetime.now().time()
        if start <= now <= end or start >= now:
            return lesson["number"]
    return None


async def get_free_cabinets(school_id, corpus_id):
    lesson_number = await get_current_lesson(school_id)
    if lesson_number is None:
        return Texts.no_current_lessons
    data = await get_request(
        "/info/cabinets/free",
        {
            "corpus_id": corpus_id,
            "day_of_week": get_current_day_of_week(),
            "lesson_number": lesson_number,
        },
    )
    if not data["data"]:
        return Texts.no_free_cabinets
    result = Texts.free_cabinets.format(
        lesson_number=lesson_number, corpus_name=await get_corpus_name_by_id(corpus_id)
    )
    for cabinet in data["data"]:
        result += cabinet["name"] + "\n"
    return result


# ~=============================
async def get_subclass_by_params(school, parallel, letter, group):
    data = await get_request(
        "/info/subclass/params",
        {
            "school_id": school,
            "educational_level": parallel,
            "identificator": letter,
            "additional_identificator": group,
        },
    )
    return data["id"]


async def register_student(telegram_id, subclass_id):
    data = await post_request(
        "/registration/student",
        {"telegram_id": telegram_id, "subclass_id": subclass_id},
    )
    await save_to_redis(telegram_id)


async def register_child(telegram_id, subclass_id):
    data = await post_request(
        "/rolemanagement/add/child",
        {"parent_id": telegram_id, "subclass_id": subclass_id},
    )
    await save_to_redis(telegram_id)


async def register_teacher(telegram_id, teacher_id):
    data = await post_request(
        "/registration/teacher", {"telegram_id": telegram_id, "teacher_id": teacher_id}
    )
    await save_to_redis(telegram_id)


async def register_parent(telegram_id):
    data = await post_request(
        "/registration/parent", {"telegram_id": telegram_id}
    )
    await save_to_redis(telegram_id)


async def register_administration(telegram_id, school_id):
    data = await post_request(
        "/registration/administration",
        {"telegram_id": telegram_id, "school_id": school_id},
    )
    await save_to_redis(telegram_id)


# ~=============================


async def get_user_roles(telegram_id):
    """
    Returns all user roles by telegram_id
    """
    data = await post_request("/rolemanagement/get", {"telegram_id": telegram_id})
    await save_to_redis(telegram_id)


# ~=============================


async def get_subclass_name_by_id(subclass_id):
    data = await get_request(f"/idgetter/subclass/{subclass_id}")
    return f"{data['educational_level']}{data['identificator']}{data['additional_identificator']}"


async def get_teacher_name_by_id(teacher_id):
    data = await get_request(f"/idgetter/teacher/{teacher_id}")
    return data["name"]


async def get_school_name_by_id(school_id):
    data = await get_request(f"/idgetter/school/{school_id}")
    return data["name"]


async def get_corpus_name_by_id(corpus_id):
    data = await get_request(f"/idgetter/corpus/{corpus_id}")
    return data["name"]


# ~=============================
async def change_role(telegram_id, subclass_id=None, teacher_id=None, school_id=None):
    if subclass_id is not None:
        data = {"telegram_id": telegram_id, "subclass_id": subclass_id}
        data = await put_request("/rolemanagement/change/student", data=data)
    elif teacher_id is not None:
        data = {"telegram_id": telegram_id, "teacher_id": teacher_id}
        data = await put_request("/rolemanagement/change/teacher", data=data)
    elif school_id is not None:
        data = {"telegram_id": telegram_id, "school_id": school_id}
        data = await put_request("/rolemanagement/change/administration", data=data)
    else:
        data = {"telegram_id": telegram_id}
        data = await put_request("/rolemanagement/change/parent", data=data)


# ~=============================
async def save_to_redis(telegram_id):
    data = await get_request("/rolemanagement/get", data={"telegram_id": telegram_id})
    for role in data["roles"]:
        if role["is_main_role"]:
            break
    if role["role_type"] == 0:  # TODO check roles
        await storage.update_data(data={"role": "Student"}, user=telegram_id)
        await storage.update_data(
            data={"subclass_id": role["data"]["subclass"]["id"]}, user=telegram_id
        )
        await storage.update_data(
            data={"parallel": role["data"]["subclass"]["educational_level"]},
            user=telegram_id,
        )
        await storage.update_data(
            data={"letter": role["data"]["subclass"]["identificator"]}, user=telegram_id
        )
        await storage.update_data(
            data={"group": role["data"]["subclass"]["additional_identificator"]},
            user=telegram_id,
        )
        await storage.update_data(
            data={"school": role["data"]["school"]["id"]}, user=telegram_id
        )
    elif role["role_type"] == 1:
        await storage.update_data(data={"role": "Teacher"}, user=telegram_id)
        await storage.update_data(
            data={"teacher": role["data"]["teacher_id"]}, user=telegram_id
        )
        await storage.update_data(
            data={"school": role["data"]["school"]["id"]}, user=telegram_id
        )
    elif role["role_type"] == 2:  # TODO parent
        await storage.update_data(data={"role": "Parent"}, user=telegram_id)
    elif role["role_type"] == 3:
        await storage.update_data(data={"role": "Administration"}, user=telegram_id)
        await storage.update_data(
            data={"school": role["data"]["school"]["id"]}, user=telegram_id
        )


# ~=============================


async def get_all_corpuses(school_id):
    data = await get_request("/info/corpuses/all", {"school_id": school_id})
    return data["data"]
