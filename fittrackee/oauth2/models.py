import time
from typing import Any, Dict, Optional

from authlib.integrations.sqla_oauth2 import (
    OAuth2AuthorizationCodeMixin,
    OAuth2ClientMixin,
    OAuth2TokenMixin,
)
from sqlalchemy.engine.base import Connection
from sqlalchemy.event import listens_for
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.orm.mapper import Mapper
from sqlalchemy.orm.session import Session

from fittrackee import db

BaseModel: DeclarativeMeta = db.Model


class OAuth2Client(BaseModel, OAuth2ClientMixin):
    __tablename__ = 'oauth2_client'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), index=True
    )
    user = db.relationship('User')

    def serialize(self, with_secret: bool = False) -> Dict:
        client = {
            'client_id': self.client_id,
            'client_description': self.client_description,
            'id': self.id,
            'issued_at': time.strftime(
                '%a, %d %B %Y %H:%M:%S GMT',
                time.gmtime(self.client_id_issued_at),
            ),
            'name': self.client_name,
            'redirect_uris': self.redirect_uris,
            'scope': self.scope,
            'website': self.client_uri,
        }
        if with_secret:
            client['client_secret'] = self.client_secret
        return client

    @property
    def client_description(self) -> Optional[str]:
        return self.client_metadata.get('client_description')


@listens_for(OAuth2Client, 'after_delete')
def on_old_oauth2_delete(
    mapper: Mapper, connection: Connection, old_oauth2_client: OAuth2Client
) -> None:
    @listens_for(db.Session, 'after_flush', once=True)
    def receive_after_flush(session: Session, context: Any) -> None:
        session.query(OAuth2AuthorizationCode).filter(
            OAuth2AuthorizationCode.client_id == old_oauth2_client.client_id
        ).delete(synchronize_session=False)
        session.query(OAuth2Token).filter(
            OAuth2Token.client_id == old_oauth2_client.client_id
        ).delete(synchronize_session=False)


class OAuth2AuthorizationCode(BaseModel, OAuth2AuthorizationCodeMixin):
    __tablename__ = 'oauth2_code'
    __table_args__ = (
        db.Index(
            'ix_oauth2_code_client_id',
            'client_id',
        ),
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), index=True
    )
    user = db.relationship('User')


class OAuth2Token(BaseModel, OAuth2TokenMixin):
    __tablename__ = 'oauth2_token'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), index=True
    )
    user = db.relationship('User')

    def is_refresh_token_active(self) -> bool:
        if self.is_revoked():
            return False
        expires_at = self.issued_at + self.expires_in * 2
        return expires_at >= time.time()

    @classmethod
    def revoke_client_tokens(cls, client_id: str) -> None:
        sql = """
            UPDATE oauth2_token
            SET access_token_revoked_at = %(revoked_at)s
            WHERE client_id = %(client_id)s;
        """
        db.engine.execute(
            sql, {'client_id': client_id, 'revoked_at': int(time.time())}
        )
        db.session.commit()
