from datetime import datetime
from typing import Dict, Optional

from flask import current_app
from sqlalchemy.types import Enum

from fittrackee import BaseModel, db

from .constants import AP_CTX
from .enums import ActorType
from .exceptions import (
    FollowRequestAlreadyProcessedError,
    NotExistingFollowRequestError,
)
from .utils import generate_keys, get_ap_url


class Domain(BaseModel):
    """ActivityPub Domain"""

    __tablename__ = 'domains'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(1000), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)
    is_allowed = db.Column(db.Boolean, default=True, nullable=False)

    actors = db.relationship('Actor', back_populates='domain')

    def __str__(self) -> str:
        return f'<Domain \'{self.name}\'>'

    def __init__(
        self, name: str, created_at: Optional[datetime] = datetime.utcnow()
    ) -> None:
        self.name = name
        self.created_at = created_at

    @property
    def is_remote(self) -> bool:
        return self.name != current_app.config['AP_DOMAIN']

    def serialize(self) -> Dict:
        return {
            'id': self.id,
            'name': self.name,
            'created_at': self.created_at,
            'is_remote': self.is_remote,
            'is_allowed': self.is_allowed,
        }


class FollowRequest(BaseModel):
    """Follow request between two actors"""

    __tablename__ = 'follow_requests'
    follower_actor_id = db.Column(
        db.Integer,
        db.ForeignKey('actors.id'),
        primary_key=True,
    )
    followed_actor_id = db.Column(
        db.Integer,
        db.ForeignKey('actors.id'),
        primary_key=True,
    )
    is_approved = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow
    )
    updated_at = db.Column(db.DateTime, nullable=True)


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
    inbox_url = db.Column(db.String(255), nullable=False)
    outbox_url = db.Column(db.String(255), nullable=False)
    followers_url = db.Column(db.String(255), nullable=False)
    following_url = db.Column(db.String(255), nullable=False)
    shared_inbox_url = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)
    manually_approves_followers = db.Column(
        db.Boolean, default=True, nullable=False
    )
    last_fetch_date = db.Column(db.DateTime, nullable=True)

    domain = db.relationship('Domain', back_populates='actors')
    user = db.relationship('User', uselist=False, back_populates='actor')

    received_follow_requests = db.relationship(
        FollowRequest,
        backref='to_actor',
        primaryjoin=id == FollowRequest.followed_actor_id,
        lazy='dynamic',
    )
    sent_follow_requests = db.relationship(
        FollowRequest,
        backref='from_actor',
        primaryjoin=id == FollowRequest.follower_actor_id,
        lazy='dynamic',
    )

    def __str__(self) -> str:
        return f'<Actor \'{self.name}\'>'

    def __init__(
        self,
        username: str,
        domain_id: int,
        created_at: Optional[datetime] = datetime.utcnow(),
        remote_user_data: Optional[Dict] = None,
    ) -> None:
        self.created_at = created_at
        self.domain_id = domain_id
        self.preferred_username = username
        if remote_user_data:
            self.activitypub_id = remote_user_data['id']
            self.followers_url = remote_user_data['followers']
            self.following_url = remote_user_data['following']
            self.inbox_url = remote_user_data['inbox']
            self.outbox_url = remote_user_data['outbox']
            self.shared_inbox_url = remote_user_data.get('endpoints', {}).get(
                'sharedInbox'
            )
        else:
            self.activitypub_id = get_ap_url(username, 'user_url')
            self.followers_url = get_ap_url(username, 'followers')
            self.following_url = get_ap_url(username, 'following')
            self.inbox_url = get_ap_url(username, 'inbox')
            self.outbox_url = get_ap_url(username, 'outbox')
            self.shared_inbox_url = get_ap_url(username, 'shared_inbox')

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
    def pending_follow_requests(self) -> FollowRequest:
        return self.received_follow_requests.filter_by(updated_at=None).all()

    def send_follow_request_to(self, target: 'Actor') -> FollowRequest:
        follow_request = FollowRequest(
            follower_actor_id=self.id, followed_actor_id=target.id
        )
        db.session.add(follow_request)
        db.session.commit()
        return follow_request

    def _processes_follow_request_from(
        self, actor: 'Actor', approved: bool
    ) -> FollowRequest:
        follow_request = FollowRequest.query.filter_by(
            follower_actor_id=actor.id, followed_actor_id=self.id
        ).first()
        if not follow_request:
            raise NotExistingFollowRequestError()
        if follow_request.updated_at is not None:
            raise FollowRequestAlreadyProcessedError()
        follow_request.is_approved = approved
        follow_request.updated_at = datetime.now()
        db.session.commit()
        return follow_request

    def approves_follow_request_from(self, actor: 'Actor') -> FollowRequest:
        follow_request = self._processes_follow_request_from(
            actor=actor, approved=True
        )
        return follow_request

    def refuses_follow_request_from(self, actor: 'Actor') -> FollowRequest:
        follow_request = self._processes_follow_request_from(
            actor=actor, approved=False
        )
        return follow_request

    def serialize(self) -> Dict:
        return {
            '@context': AP_CTX,
            'id': self.activitypub_id,
            'type': self.type.value,
            'preferredUsername': self.preferred_username,
            'name': self.name,
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
