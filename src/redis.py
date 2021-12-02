async def get_school_name(telegram_id):
    """
    Return school name where `main_role` of account with `telegram_id` is
    """
    # TODO Implement
    return "1580"


async def get_school_id(telegram_id):
    """
    Return school id where `main_role` of account with `telegram_id` is
    """
    # TODO Implement
    return 1


async def get_teacher_name(telegram_id):
    """
    Return teacher name for account with `telegram_id` (`main_role`?)
    """
    # TODO Implement
    return "Иванов К. Ю."


async def get_student_class(telegram_id):
    """
    Returns subclass string for account with `telegram_id` (`main_role`?)
    """
    # TODO Implement
    return "11Е1"


async def get_subclass_id(telegram_id):
    """
    Returns subclass_id for account with `telegram_id` (`main_role`?)
    """
    # TODO Implement
    return 1


async def get_teacher_id(telegram_id):
    """
    Return teacher id for account with `telegram_id` (`main_role`?)
    """
    # TODO Implement
    return 1


async def get_main_role(telegram_id):
    """
    Return main role for account with `telegram_id`
    """
    # TODO Implement
    return "teacher"


async def get_children(name: int):
    return {"child 1": "id1", "child 2": "id2"}


async def save(full_user_info):
    pass
