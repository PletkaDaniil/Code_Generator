import secrets


def generate_code() -> str:
    """
        Формируем случайное четырёхзначное число от 1000 до 9999
    """
    return str(secrets.randbelow(9000) + 1000)