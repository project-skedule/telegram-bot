from datetime import datetime
from typing import Union

import aiohttp
import ujson
from aiogram.utils import markdown
from loguru import logger

from src.constants import DAYS_OF_WEEK
from src.redis import (
    get_main_role,
    get_school_id,
    get_subclass_id,
    get_teacher_id,
    storage,
)
from src.texts import Texts
from src.config import URL
from src.token import Token


api_token = Token()


def get_current_day_of_week():
    return datetime.today().weekday() + 1


async def get_request(request: str, data=None):
    logger.debug(f"get_request to {URL}/api{request} with data: {data}")
    headers = {"Authorization": f"Bearer {api_token.get_token()}"}
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(f"{URL}/api{request}", params=data) as response:
            response = await response.read()
            answer = ujson.loads(response)
            logger.debug(f"answer to request: {answer}")
            return answer


async def post_request(request: str, data=None):
    logger.debug(f"post_request to {URL}/api{request} with data: {data}")
    headers = {"Authorization": f"Bearer {api_token.get_token()}"}
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.post(f"{URL}/api{request}", json=data) as response:
            response = await response.read()
            answer = ujson.loads(response)
            logger.debug(f"answer to request: {answer}")
            return answer


async def put_request(request: str, data=None):
    logger.debug(f"put_request to {URL}/api{request} with data: {data}")
    headers = {"Authorization": f"Bearer {api_token.get_token()}"}
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.put(f"{URL}/api{request}", json=data) as response:
            response = await response.read()
            answer = ujson.loads(response)
            logger.debug(f"answer to request: {answer}")
            return answer


# ~=============================


async def get_user_today(
    telegram_id, is_searching=False, teacher_id=None, subclass_id=None, child_name=None
):
    return await get_user_day_of_week(
        telegram_id,
        get_current_day_of_week(),
        is_searching=is_searching,
        teacher_id=teacher_id,
        subclass_id=subclass_id,
        child_name=child_name,
    )


async def get_user_tomorrow(
    telegram_id, is_searching=False, teacher_id=None, subclass_id=None, child_name=None
):
    return await get_user_day_of_week(
        telegram_id,
        get_current_day_of_week() % 7 + 1,
        is_searching=is_searching,
        teacher_id=teacher_id,
        subclass_id=subclass_id,
        child_name=child_name,
    )


async def get_student_day_of_week(
    telegram_id, day_of_week, subclass_id, subclass_name=None, child_name=None
):
    school_id = await get_school_id(telegram_id)

    data = await get_request(
        "/lesson/get/day",
        data={
            "subclass_id": subclass_id,
            "school_id": school_id,
            "day_of_week": day_of_week,
        },
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
        if child_name is not None:
            return f'У ребёнка "{child_name}" нет уроков *{day_of_week}*\n'
        elif subclass_name is not None:
            return f'У класса "{subclass_name}" нет уроков *{day_of_week}*\n'
        else:
            return f"У вас нет уроков *{day_of_week}*\n"
    else:
        if child_name is not None:
            return f'Расписание ребёнка "{child_name}" *{day_of_week}*:\n' + result
        elif subclass_name is not None:
            return f'Расписание класса "{subclass_name}" *{day_of_week}*:\n' + result
        else:
            return f"Ваше расписание *{day_of_week}*:\n" + result


async def get_teacher_day_of_week(
    telegram_id, day_of_week, teacher_id, teacher_name=None
):
    school_id = await get_school_id(telegram_id)

    data = await get_request(
        "/lesson/get/day",
        data={
            "teacher_id": teacher_id,
            "school_id": school_id,
            "day_of_week": day_of_week,
        },
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
    telegram_id,
    day_of_week,
    is_searching=False,
    teacher_id=None,
    subclass_id=None,
    child_name=None,
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
                telegram_id, day_of_week, subclass_id, subclass_name, child_name
            )
    else:
        main_role = await get_main_role(telegram_id)

        if main_role == "Teacher":
            return await get_teacher_day_of_week(
                telegram_id, day_of_week, await get_teacher_id(telegram_id)
            )
        else:
            return await get_student_day_of_week(
                telegram_id,
                day_of_week,
                await get_subclass_id(telegram_id),
            )


async def get_student_week(
    telegram_id, subclass_id, subclass_name=None, child_name=None
):
    school_id = await get_school_id(telegram_id)

    data = await get_request(
        "/lesson/get/range",
        data={
            "subclass_id": subclass_id,
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
        if child_name is not None:
            result += markdown.underline(
                f'Расписание ребёнка "{child_name}" {name_day}:\n'
            )
        elif subclass_name is not None:
            result += markdown.underline(
                f'Расписание класса "{subclass_name}" {name_day}:\n'
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

    data = await get_request(
        "/lesson/get/range",
        data={
            "teacher_id": teacher_id,
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
                f"Расписание учителя {teacher_name} {name_day}:\n"
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
    telegram_id, is_searching=False, teacher_id=None, subclass_id=None, child_name=None
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
            return await get_student_week(
                telegram_id, subclass_id, subclass_name, child_name
            )
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


async def get_ring_timetable(telegram_id: int = None, school_id=None):
    if school_id is None:
        school_id = await get_school_id(telegram_id)
    data = await get_request(
        "/info/lessontimetables/all", data={"school_id": school_id}
    )
    return data["data"]


async def get_canteen_timetable(telegram_id: int = None, school_id=None):
    if school_id is None:
        school_id = await get_school_id(telegram_id)
    corpora = await get_request("/info/corpuses/all", data={"school_id": school_id})
    corpora = list(map(lambda c: (c["name"], c["id"]), corpora["data"]))
    result = markdown.escape_md(Texts.canteen_timetable_header)
    for corpus_name, corpus_id in corpora:
        canteen_text = (
            await get_request("/info/corpus/canteen", data={"corpus_id": corpus_id})
        )["data"]
        result += markdown.underline(corpus_name) + "\n\n"
        result += markdown.escape_md(canteen_text) + "\n\n"

    return result


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
    if data is None:
        return False
    return data["data"]


async def get_similar_schools(school):
    data = await get_request("/info/schools/distance", {"name": school})
    logger.debug(f"get_similar_schools for {school}; answer: {data}")
    return data["data"]


async def get_similar_teachers(teacher_name, school_id):
    data = await get_request(
        "/info/teachers/distance", {"name": teacher_name, "school_id": school_id}
    )
    return data["data"]


async def get_current_lesson(school_id):
    data = await get_request("/info/lessontimetables/all", {"school_id": school_id})
    now = datetime.now().time()
    first_lesson_start = datetime.strptime(
        data["data"][0]["time_start"], "%H:%M"
    ).time()
    if now < first_lesson_start:
        return
    for lesson in data["data"]:
        start = datetime.strptime(lesson["time_start"], "%H:%M").time()
        end = datetime.strptime(lesson["time_end"], "%H:%M").time()
        if start <= now <= end or start >= now:
            return lesson["number"]
    return


async def get_free_cabinets(school_id, corpus_id, corpus_name, lesson_number):
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
    return data["data"]
    if not data["data"]:
        return Texts.no_free_cabinets
    result = Texts.free_cabinets.format(
        lesson_number=lesson_number, corpus_name=corpus_name
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


async def register_child(telegram_id, subclass_id, name):
    data = await put_request(
        "/rolemanagement/add/child",
        {"telegram_id": telegram_id, "subclass_id": subclass_id},
    )

    school_id = data["school"]["id"]
    child_id = data["child_id"]

    storage_data = (await storage.get_data(user=telegram_id))["children"]
    storage_data.append(
        {
            "name": name,
            "subclass_id": subclass_id,
            "school_id": school_id,
            "child_id": child_id,
        }
    )
    await storage.update_data(data={"children": storage_data}, user=telegram_id)
    logger.debug(f"{await storage.get_data(user=telegram_id)}")


async def delete_child(telegram_id, child_id):
    data = await put_request(
        "/rolemanagement/delete/child",
        {"telegram_id": telegram_id, "child_id": child_id},
    )

    children = (await storage.get_data(user=telegram_id))["children"]
    for child in children:
        if child["child_id"] == child_id:
            children.remove(child)
            break
    await storage.update_data(data={"children": children}, user=telegram_id)


async def register_teacher(telegram_id, teacher_id):
    data = await post_request(
        "/registration/teacher", {"telegram_id": telegram_id, "teacher_id": teacher_id}
    )
    await save_to_redis(telegram_id)


async def register_parent(telegram_id):
    data = await post_request("/registration/parent", {"telegram_id": telegram_id})
    await save_to_redis(telegram_id)


async def register_administration(telegram_id, school_id):
    data = await post_request(
        "/registration/administration",
        {"telegram_id": telegram_id, "school_id": school_id},
    )
    await save_to_redis(telegram_id)


# ~=============================


async def get_role_id(telegram_id):
    data = await post_request("/rolemanagement/get", {"telegram_id": telegram_id})

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

    await storage.set_data(data={}, user=telegram_id)
    await save_to_redis(telegram_id)


# ~=============================
async def save_to_redis(telegram_id):
    data = await get_request("/rolemanagement/get", data={"telegram_id": telegram_id})
    await storage.update_data(
        data={"premium_status": data["premium_status"]}, user=telegram_id
    )
    for role in data["roles"]:
        if role["is_main_role"]:
            break
    if role["role_type"] == 0:  # Student
        await storage.update_data(
            data={
                "role": "Student",
                "subclass_id": role["data"]["subclass"]["id"],
                "parallel": role["data"]["subclass"]["educational_level"],
                "letter": role["data"]["subclass"]["identificator"],
                "group": role["data"]["subclass"]["additional_identificator"],
                "school": role["data"]["school"]["id"],
            },
            user=telegram_id,
        )

    elif role["role_type"] == 1:  # Teacher
        await storage.update_data(
            data={
                "role": "Teacher",
                "teacher": role["data"]["teacher_id"],
                "school": role["data"]["school"]["id"],
            },
            user=telegram_id,
        )

    elif role["role_type"] == 2:  # Parent
        await storage.update_data(data={"role": "Parent"}, user=telegram_id)
        if (await storage.get_data(user=telegram_id)).get("children") is None:
            await storage.update_data(data={"children": []}, user=telegram_id)

    elif role["role_type"] == 3:  # Administration
        await storage.update_data(
            data={"role": "Administration", "school": role["data"]["school"]["id"]},
            user=telegram_id,
        )

async def get_main_role_id(telegram_id):
    data = await get_request("/rolemanagement/get", data={"telegram_id": telegram_id})
    for role in data["roles"]:
        if role["is_main_role"]:
            return role["id"]

# ~=============================


async def get_all_corpuses(school_id):
    data = await get_request("/info/corpuses/all", {"school_id": school_id})
    return data["data"]
