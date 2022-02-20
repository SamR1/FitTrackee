import random
import string
from typing import Optional


def random_string(length: Optional[int] = None) -> str:
    if length is None:
        length = 10
    return ''.join(
        random.choice(string.ascii_letters + string.digits)
        for _ in range(length)
    )


def random_domain() -> str:
    return f'https://{random_string()}.social'
