from loguru import logger

from .bot import storage


async def get_school_id(telegram_id):
    """
    Return school id where `main_role` of account with `telegram_id` is
    """
    return (await storage.get_data(user=telegram_id))["school"]


async def get_subclass_id(telegram_id):
    """
    Returns subclass_id for user
    """
    logger.debug("get_subclass_id")
    return (await storage.get_data(user=telegram_id))["subclass_id"]


async def get_teacher_id(telegram_id):
    """
    Return teacher id for user
    """
    return (await storage.get_data(user=telegram_id))["teacher"]


async def get_main_role(telegram_id):
    """
    Return main role for user
    """
    return (await storage.get_data(user=telegram_id))["role"]


async def get_children(telegram_id: int):
    data = (await storage.get_data(user=telegram_id))["children"]
    answer = []
    for child in data:
        answer.append(
            {
                "name": child["name"],
                "subclass_id": child["subclass_id"],
                "school_id": child["school_id"],
                "child_id": child["child_id"],
            }
        )

    return answer


async def get_premium_status(telegram_id: int):
    data = (await storage.get_data(user=telegram_id))["premium_status"]

    return data


async def get_child_by_id(telegram_id: int, child_id: int):
    children = (await storage.get_data(user=telegram_id))["children"]
    for child in children:
        if child["child_id"] == child_id:
            return child
