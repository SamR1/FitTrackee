from flask import Flask

from fittrackee.oauth2.models import OAuth2Client

from ..mixins import RandomMixin


class TestOAuthClientSerialize(RandomMixin):
    def test_it_returns_oauth_client(self, app: Flask) -> None:
        oauth_client = OAuth2Client(
            id=self.random_int(),
            client_id=self.random_string(),
            client_id_issued_at=1653738796,
        )
        oauth_client.set_client_metadata(
            {
                'client_name': self.random_string(),
                'client_description': self.random_string(),
                'redirect_uris': [self.random_string()],
                'client_uri': self.random_domain(),
            }
        )

        serialized_oauth_client = oauth_client.serialize()

        assert serialized_oauth_client['client_id'] == oauth_client.client_id
        assert (
            serialized_oauth_client['client_description']
            == oauth_client.client_description
        )
        assert 'client_secret' not in serialized_oauth_client
        assert (
            serialized_oauth_client['issued_at']
            == 'Sat, 28 May 2022 11:53:16 GMT'
        )
        assert serialized_oauth_client['id'] == oauth_client.id
        assert serialized_oauth_client['name'] == oauth_client.client_name
        assert (
            serialized_oauth_client['redirect_uris']
            == oauth_client.redirect_uris
        )
        assert serialized_oauth_client['scope'] == oauth_client.scope
        assert serialized_oauth_client['website'] == oauth_client.client_uri

    def test_it_returns_oauth_client_with_client_secret(
        self, app: Flask
    ) -> None:
        oauth_client = OAuth2Client(
            id=self.random_int(),
            client_id=self.random_string(),
            client_id_issued_at=self.random_int(),
        )
        oauth_client.set_client_metadata(
            {
                'client_name': self.random_string(),
                'redirect_uris': [self.random_string()],
                'client_uri': self.random_domain(),
            }
        )

        serialized_oauth_client = oauth_client.serialize(with_secret=True)

        assert (
            serialized_oauth_client['client_secret']
            == oauth_client.client_secret
        )
