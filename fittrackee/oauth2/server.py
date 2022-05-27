from authlib.integrations.flask_oauth2 import AuthorizationServer
from authlib.integrations.sqla_oauth2 import (
    create_query_client_func,
    create_save_token_func,
)

from fittrackee import db

from .models import OAuth2Client, OAuth2Token

query_client = create_query_client_func(db.session, OAuth2Client)
save_token = create_save_token_func(db.session, OAuth2Token)
authorization_server = AuthorizationServer(
    query_client=query_client,
    save_token=save_token,
)
