import re


def is_valid_email(email: str) -> bool:
    """
    Return if email format is valid
    """
    if not email:
        return False
    mail_pattern = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
    return re.match(mail_pattern, email) is not None


def check_password(password: str) -> str:
    """
    Verify if password have more than 8 characters
    If not, it returns error message
    """
    if len(password) < 8:
        return 'password: 8 characters required\n'
    return ''


def check_username(username: str) -> str:
    """
    Return if username is valid
    If not, it returns error messages
    """
    ret = ''
    if not (2 < len(username) < 31):
        ret += 'username: 3 to 30 characters required\n'
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        ret += (
            'username: only alphanumeric characters and the '
            'underscore character "_" allowed\n'
        )
    return ret


def register_controls(username: str, email: str, password: str) -> str:
    """
    Verify if username, email and passwords are valid
    If not, it returns error messages
    """
    ret = check_username(username)
    if not is_valid_email(email):
        ret += 'email: valid email must be provided\n'
    ret += check_password(password)
    return ret
