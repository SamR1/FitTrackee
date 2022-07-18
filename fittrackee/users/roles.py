from enum import Enum


class UserRole(Enum):
    ADMIN = 'admin'
    AUTH_USER = 'auth_user'
    USER = 'user'
