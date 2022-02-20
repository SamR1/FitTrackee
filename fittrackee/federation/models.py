from datetime import datetime
from typing import Dict, Optional

from flask import current_app
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.types import Enum

from fittrackee import db
from fittrackee.users.models import User

from .utils import ACTOR_TYPES, AP_CTX, generate_keys, get_ap_url

BaseModel: DeclarativeMeta = db.Model


class Actor(BaseModel):
    """ActivityPub Actor"""

    __tablename__ = 'actors'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ap_id = db.Column(db.String(255), unique=True, nullable=False)
    user_id = db.Column(
        db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False
    )
    type = db.Column(
        Enum(*ACTOR_TYPES, name='actor_types'), server_default='Person'
    )
    domain = db.Column(db.String(1000), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    preferred_username = db.Column(db.String(255), nullable=False)
    public_key = db.Column(db.String(5000), nullable=True)
    private_key = db.Column(db.String(5000), nullable=True)
    inbox_url = db.Column(db.String(255), nullable=False)
    outbox_url = db.Column(db.String(255), nullable=False)
    followers_url = db.Column(db.String(255), nullable=False)
    following_url = db.Column(db.String(255), nullable=False)
    shared_inbox_url = db.Column(db.String(255), nullable=False)
    is_remote = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)
    manually_approves_followers = db.Column(
        db.Boolean, default=True, nullable=False
    )
    last_fetch_date = db.Column(db.DateTime, nullable=True)

    def __str__(self) -> str:
        return f'<Actor \'{self.name}\'>'

    def __init__(
        self,
        user: User,
        created_at: Optional[datetime] = datetime.utcnow(),
        is_remote: Optional[bool] = False,
    ) -> None:
        self.ap_id = get_ap_url(user.username, 'user_url')
        self.created_at = created_at
        self.domain = f"{current_app.config['AP_DOMAIN']}"
        self.followers_url = get_ap_url(user.username, 'followers')
        self.following_url = get_ap_url(user.username, 'following')
        self.inbox_url = get_ap_url(user.username, 'inbox')
        self.is_remote = is_remote
        self.name = user.username
        self.outbox_url = get_ap_url(user.username, 'outbox')
        self.preferred_username = user.username
        self.shared_inbox_url = get_ap_url(user.username, 'shared_inbox')
        self.user_id = user.id

    def generate_keys(self) -> None:
        self.public_key, self.private_key = generate_keys()

    def serialize(self) -> Dict:
        return {
            '@context': AP_CTX,
            'id': self.ap_id,
            'type': self.type,
            'preferredUsername': self.preferred_username,
            'name': self.name,
            'inbox': self.inbox_url,
            'outbox': self.outbox_url,
            'followers': self.followers_url,
            'following': self.following_url,
            'manuallyApprovesFollowers': self.manually_approves_followers,
            'publicKey': {
                'id': f'{self.ap_id}#main-key',
                'owner': self.ap_id,
                'publicKeyPem': self.public_key,
            },
            'endpoints': {'sharedInbox': self.shared_inbox_url},
        }
