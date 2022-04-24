from datetime import datetime
from typing import Any, Dict, Optional

from flask import current_app
from sqlalchemy.engine.base import Connection
from sqlalchemy.event import listens_for
from sqlalchemy.orm.mapper import Mapper
from sqlalchemy.orm.session import Session
from sqlalchemy.types import Enum

from fittrackee import VERSION, BaseModel, db

from .constants import AP_CTX
from .enums import ActorType
from .utils import generate_keys, get_ap_url

MEDIA_TYPES = {
    'gif': 'image/gif',
    'jpg': 'image/jpeg',
    'png': 'image/png',
}


class Domain(BaseModel):
    """ActivityPub Domain"""

    __tablename__ = 'domains'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(1000), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)
    is_allowed = db.Column(db.Boolean, default=True, nullable=False)
    software_name = db.Column(db.String(255), nullable=True)
    software_version = db.Column(db.String(255), nullable=True)

    actors = db.relationship('Actor', back_populates='domain')

    def __str__(self) -> str:
        return f'<Domain \'{self.name}\'>'

    def __init__(
        self,
        name: str,
        created_at: Optional[datetime] = None,
        software_name: Optional[str] = None,
        software_version: Optional[str] = None,
    ) -> None:
        self.name = name
        self.created_at = (
            datetime.utcnow() if created_at is None else created_at
        )
        self.software_name = software_name
        self.software_version = software_version

    @property
    def is_remote(self) -> bool:
        return self.name != current_app.config['AP_DOMAIN']

    @property
    def software_current_version(self) -> bool:
        return self.software_version if self.is_remote else VERSION

    def serialize(self) -> Dict:
        return {
            'id': self.id,
            'name': self.name,
            'created_at': self.created_at,
            'is_remote': self.is_remote,
            'is_allowed': self.is_allowed,
            'software_name': self.software_name,
            'software_version': self.software_current_version,
        }


class Actor(BaseModel):
    """ActivityPub Actor"""

    __tablename__ = 'actors'
    __table_args__ = (
        db.UniqueConstraint(
            'domain_id', 'preferred_username', name='domain_username_unique'
        ),
    )
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    activitypub_id = db.Column(db.String(255), unique=True, nullable=False)
    domain_id = db.Column(
        db.Integer, db.ForeignKey('domains.id'), nullable=False
    )
    type = db.Column(
        Enum(ActorType, name='actor_types'), server_default='PERSON'
    )
    preferred_username = db.Column(db.String(255), nullable=False)
    public_key = db.Column(db.String(5000), nullable=True)
    private_key = db.Column(db.String(5000), nullable=True)
    profile_url = db.Column(db.String(255), nullable=False)
    inbox_url = db.Column(db.String(255), nullable=False)
    outbox_url = db.Column(db.String(255), nullable=False)
    followers_url = db.Column(db.String(255), nullable=False)
    following_url = db.Column(db.String(255), nullable=False)
    shared_inbox_url = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)
    last_fetch_date = db.Column(db.DateTime, nullable=True)

    domain = db.relationship('Domain', back_populates='actors')
    user = db.relationship('User', uselist=False, back_populates='actor')
    stats = db.relationship(
        'RemoteActorStats', cascade='all, delete', uselist=False
    )

    def __str__(self) -> str:
        return f'<Actor \'{self.name}\'>'

    def __init__(
        self,
        preferred_username: str,
        domain_id: int,
        created_at: Optional[datetime] = None,
        remote_user_data: Optional[Dict] = None,
    ) -> None:
        self.created_at = (
            datetime.utcnow() if created_at is None else created_at
        )
        self.domain_id = domain_id
        self.preferred_username = preferred_username
        if remote_user_data:
            self.update_remote_data(remote_user_data)
        else:
            self.activitypub_id = get_ap_url(preferred_username, 'user_url')
            self.followers_url = get_ap_url(preferred_username, 'followers')
            self.following_url = get_ap_url(preferred_username, 'following')
            self.profile_url = get_ap_url(preferred_username, 'profile_url')
            self.inbox_url = get_ap_url(preferred_username, 'inbox')
            self.outbox_url = get_ap_url(preferred_username, 'outbox')
            self.shared_inbox_url = get_ap_url(
                preferred_username, 'shared_inbox'
            )
            self.generate_keys()

    @classmethod
    def generate_stats_if_remote(
        cls, actor_id: int, domain_id: int, session: Session
    ) -> None:
        domain = Domain.query.filter_by(id=domain_id).first()
        if domain.name != current_app.config['AP_DOMAIN']:
            stats = RemoteActorStats(actor_id=actor_id)
            session.add(stats)

    def generate_keys(self) -> None:
        self.public_key, self.private_key = generate_keys()

    @property
    def is_remote(self) -> bool:
        return self.domain.is_remote

    @property
    def name(self) -> Optional[str]:
        if self.type == ActorType.PERSON and self.user:
            return self.user.username
        return None

    @property
    def fullname(self) -> Optional[str]:
        if self.type == ActorType.PERSON:
            return f'{self.preferred_username}@{self.domain.name}'
        return None

    @property
    def manually_approves_followers(self) -> Optional[bool]:
        if self.type == ActorType.PERSON and self.user:
            return self.user.manually_approves_followers
        return None

    def update_remote_data(self, remote_user_data: Dict) -> None:
        self.activitypub_id = remote_user_data['id']
        self.type = ActorType(remote_user_data['type'])
        self.followers_url = remote_user_data['followers']
        self.following_url = remote_user_data['following']
        self.profile_url = remote_user_data.get('url', remote_user_data['id'])
        self.inbox_url = remote_user_data['inbox']
        self.outbox_url = remote_user_data['outbox']
        self.shared_inbox_url = remote_user_data.get('endpoints', {}).get(
            'sharedInbox'
        )
        self.public_key = remote_user_data['publicKey']['publicKeyPem']
        self.last_fetch_date = datetime.utcnow()

    def serialize(self) -> Dict:
        actor_dict = {
            '@context': AP_CTX,
            'id': self.activitypub_id,
            'type': self.type.value,
            'preferredUsername': self.preferred_username,
            'name': self.name,
            'url': self.profile_url,
            'inbox': self.inbox_url,
            'outbox': self.outbox_url,
            'followers': self.followers_url,
            'following': self.following_url,
            'manuallyApprovesFollowers': self.manually_approves_followers,
            'publicKey': {
                'id': f'{self.activitypub_id}#main-key',
                'owner': self.activitypub_id,
                'publicKeyPem': self.public_key,
            },
            'endpoints': {'sharedInbox': self.shared_inbox_url},
        }
        if self.user.picture:
            extension = self.user.picture.rsplit('.', 1)[1].lower()
            actor_dict['icon'] = {
                'type': 'Image',
                'mediaType': MEDIA_TYPES[extension],
                'url': (
                    f'https://{current_app.config["AP_DOMAIN"]}'
                    f'/api/users/{self.user.username}/picture'
                ),
            }
        return actor_dict


@listens_for(Actor, 'after_insert')
def on_actor_insert(
    mapper: Mapper, connection: Connection, actor: Actor
) -> None:
    @listens_for(db.Session, 'after_flush', once=True)
    def receive_after_flush(session: Session, context: Any) -> None:
        Actor.generate_stats_if_remote(
            actor_id=actor.id, domain_id=actor.domain_id, session=session
        )


class RemoteActorStats(BaseModel):
    """ActivityPub Remote Actor statistics"""

    __tablename__ = 'remote_actors_stats'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    actor_id = db.Column(
        db.Integer,
        db.ForeignKey('actors.id'),
        nullable=False,
        index=True,
        unique=True,
    )
    items = db.Column(db.Integer, default=0, nullable=False)
    followers = db.Column(db.Integer, default=0, nullable=False)
    following = db.Column(db.Integer, default=0, nullable=False)

    def __init__(self, actor_id: int) -> None:
        self.actor_id = actor_id
