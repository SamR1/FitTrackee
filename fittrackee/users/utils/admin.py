from fittrackee import db

from ..exceptions import UserNotFoundException
from ..models import User


def set_admin_rights(username: str) -> None:
    user = User.query.filter_by(username=username).first()
    if not user:
        raise UserNotFoundException()
    user.admin = True
    user.is_active = True
    user.confirmation_token = None
    db.session.commit()
