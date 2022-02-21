from .bot import storage
from .logger import logger


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


async def get_children(name: int):
    return {"child 1": "id1", "child 2": "id2"}
