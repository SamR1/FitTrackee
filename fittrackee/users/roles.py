from enum import Enum
from typing import List, Optional


class UserRole(Enum):
    OWNER = 100
    ADMIN = 50
    MODERATOR = 30
    AUTH_USER = 20  # only for app (not used in database)
    USER = 10

    @classmethod
    def values(cls) -> List[int]:
        return [e.value for e in cls]

    @classmethod
    def db_values(cls) -> List[str]:
        return [str(e.value) for e in cls if e.name != "AUTH_USER"]

    @classmethod
    def db_choices(cls) -> List[str]:
        return [e.name.lower() for e in cls if e.name != "AUTH_USER"]


def has_role_rights(role: Optional[UserRole], expected_role: UserRole) -> bool:
    return role is not None and role.value >= expected_role.value


def has_moderator_rights(role: Optional[UserRole]) -> bool:
    return has_role_rights(role, UserRole.MODERATOR)


def has_admin_rights(role: Optional[UserRole]) -> bool:
    return has_role_rights(role, UserRole.ADMIN)


def is_auth_user(role: Optional[UserRole]) -> bool:
    return role is not None and role == UserRole.AUTH_USER
