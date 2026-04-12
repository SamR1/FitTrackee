import json
import os
import uuid
from io import BytesIO
from typing import TYPE_CHECKING
from unittest.mock import patch

from fittrackee import db
from fittrackee.media.models import MEDIA_DESCRIPTION_MAX_CHARACTERS, Media

from ..mixins import ApiTestCaseMixin, MediaMixin

if TYPE_CHECKING:
    from flask import Flask

    from fittrackee.users.models import User


class TestMediaGet(ApiTestCaseMixin, MediaMixin):
    route = "/media/{filename}"

    def test_it_returns_404_when_media_not_found(self, app: "Flask") -> None:
        client = app.test_client()

        response = client.get(self.route.format(filename="img.jpg"))

        self.assert_404_with_message(response, "media not found")

    def test_it_calls_send_from_directory_if_media_exists(
        self, app: "Flask", user_1: "User"
    ) -> None:
        media = self.create_media(user_1)
        client = app.test_client()
        with patch(
            "fittrackee.media.routes.send_from_directory",
            return_value="file",
        ) as mock:
            response = client.get(
                self.route.format(filename=media.file_name),
            )

        assert response.status_code == 200
        mock.assert_called_once_with(
            app.config["UPLOAD_FOLDER"], f"media/{user_1.id}/{media.file_name}"
        )

    def test_it_calls_send_from_directory_if_thumbnail_exists(
        self, app: "Flask", user_1: "User"
    ) -> None:
        media = self.create_media(user_1)
        client = app.test_client()
        with patch(
            "fittrackee.media.routes.send_from_directory",
            return_value="file",
        ) as mock:
            response = client.get(
                self.route.format(filename=media.thumbnail),
            )

        assert response.status_code == 200
        mock.assert_called_once_with(
            app.config["UPLOAD_FOLDER"],
            f"media/{user_1.id}/{media.thumbnail}",
        )


class TestMediaApiPost(ApiTestCaseMixin):
    route = "/api/media"

    def test_it_returns_401_when_user_is_not_authenticated(
        self, app: "Flask"
    ) -> None:
        client = app.test_client()

        response = client.post(
            self.route, headers={"content_type": "multipart/form-data"}
        )

        self.assert_401(response)

    def test_it_returns_403_when_user_is_suspended(
        self, app: "Flask", suspended_user: "User"
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, suspended_user.email
        )

        response = client.post(
            self.route,
            headers={
                "content_type": "multipart/form-data",
                "Authorization": f"Bearer {auth_token}",
            },
        )

        self.assert_403(response)

    def test_it_returns_400_if_file_is_missing(
        self, app: "Flask", user_1: "User"
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            self.route,
            headers={
                "content_type": "multipart/form-data",
                "Authorization": f"Bearer {auth_token}",
            },
        )

        self.assert_400(response, "no file part", "fail")

    def test_it_returns_400_if_file_extension_is_invalid(
        self, app: "Flask", user_1: "User"
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            self.route,
            data=dict(file=(BytesIO(b"avatar"), "img.bmp")),
            headers={
                "content_type": "multipart/form-data",
                "Authorization": f"Bearer {auth_token}",
            },
        )

        self.assert_400(response, "file extension not allowed", "fail")

    def test_it_returns_400_if_image_size_exceeds_file_limit(
        self, app_with_max_zip_file_size: "Flask", user_1: "User"
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app_with_max_zip_file_size, user_1.email
        )

        response = client.post(
            self.route,
            data=dict(
                file=(BytesIO(b"test_file_for_image" * 50), "image.jpg")
            ),
            headers={
                "content_type": "multipart/form-data",
                "Authorization": f"Bearer {auth_token}",
            },
        )

        data = self.assert_413(
            response,
            "Error during media upload, file size (1.2KB) exceeds 1.0KB.",
        )
        assert "data" not in data

    def test_it_returns_400_if_file_content_is_invalid(
        self, app: "Flask", user_1: "User"
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.post(
            self.route,
            data=dict(file=(BytesIO(b"invalid_content"), "img.jpg")),
            headers={
                "content_type": "multipart/form-data",
                "Authorization": f"Bearer {auth_token}",
            },
        )

        self.assert_400(response, "error when reading media file", "error")

    def test_it_creates_media(self, app: "Flask", user_1: "User") -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )
        file_path = os.path.join(
            app.root_path, "tests/files/image_with_gps_exif.jpg"
        )
        with (
            open(file_path, "rb") as image_file,
            patch.object(uuid, "uuid4") as uuid4_mock,
        ):
            uuid4_mock.return_value.hex = "76hsd9"

            response = client.post(
                self.route,
                data=dict(file=(BytesIO(image_file.read()), "avatar.png")),
                headers=dict(
                    content_type="multipart/form-data",
                    Authorization=f"Bearer {auth_token}",
                ),
            )

        assert response.status_code == 201
        media = Media.query.one()

        data = json.loads(response.data.decode())
        assert data == media.serialize()

    def test_expected_scope_is_media_write(
        self, app: "Flask", user_1: "User"
    ) -> None:
        self.assert_response_scope(
            app=app,
            user=user_1,
            client_method="post",
            endpoint=self.route,
            invalid_scope="profile:read",
            expected_endpoint_scope="media:write",
        )


class TestMediaApiPatch(ApiTestCaseMixin, MediaMixin):
    route = "/api/media/{media_short_id}"

    def test_it_returns_401_when_user_is_not_authenticated(
        self, app: "Flask"
    ) -> None:
        client = app.test_client()

        response = client.patch(
            self.route.format(media_short_id="self.random_short_id()"),
            json={"description": "new description"},
        )

        self.assert_401(response)

    def test_it_returns_403_when_user_is_suspended(
        self, app: "Flask", suspended_user: "User"
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, suspended_user.email
        )

        response = client.patch(
            self.route.format(media_short_id=self.random_short_id()),
            json={"description": "new description"},
            headers={
                "Authorization": f"Bearer {auth_token}",
            },
        )

        self.assert_403(response)

    def test_it_returns_404_when_media_not_found(
        self, app: "Flask", user_1: "User"
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.patch(
            self.route.format(media_short_id=self.random_short_id()),
            json={"description": "new description"},
            headers={
                "Authorization": f"Bearer {auth_token}",
            },
        )

        self.assert_404_with_message(response, "media not found")

    def test_it_returns_403_when_user_is_not_media_owner(
        self, app: "Flask", user_1: "User", user_2: "User"
    ) -> None:
        media = self.create_media(user_2)
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.patch(
            self.route.format(media_short_id=media.short_id),
            json={"description": "new description"},
            headers={
                "Authorization": f"Bearer {auth_token}",
            },
        )
        self.assert_403(response)

    def test_it_returns_400_when_payload_is_empty(
        self, app: "Flask", user_1: "User"
    ) -> None:
        media = self.create_media(user_1)
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.patch(
            self.route.format(media_short_id=media.short_id),
            json={},
            headers={
                "Authorization": f"Bearer {auth_token}",
            },
        )

        self.assert_400(response, "invalid payload")

    def test_it_updates_media_description_with_sanitized_value(
        self, app: "Flask", user_1: "User"
    ) -> None:
        media = self.create_media(user_1)
        new_description = (
            "my <span>description</span> <script>alert('evil!')</script>"
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.patch(
            self.route.format(media_short_id=media.short_id),
            json={"description": new_description},
            headers={
                "Authorization": f"Bearer {auth_token}",
            },
        )

        assert response.status_code == 200
        db.session.refresh(media)
        assert media.description == "my description "
        data = json.loads(response.data.decode())
        assert data == media.serialize()

    def test_it_empties_media_description(
        self, app: "Flask", user_1: "User"
    ) -> None:
        media = self.create_media(user_1)
        media.description = self.random_string()
        db.session.commit()
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.patch(
            self.route.format(media_short_id=media.short_id),
            json={"description": ""},
            headers={
                "Authorization": f"Bearer {auth_token}",
            },
        )

        assert response.status_code == 200
        db.session.refresh(media)
        assert media.description == ""

    def test_test_it_updates_media_description_when_it_exceeds_max_limit(
        self, app: "Flask", user_1: "User"
    ) -> None:
        media = self.create_media(user_1)
        new_description = self.random_string(
            length=MEDIA_DESCRIPTION_MAX_CHARACTERS + 1
        )
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.patch(
            self.route.format(media_short_id=media.short_id),
            json={"description": new_description},
            headers={
                "Authorization": f"Bearer {auth_token}",
            },
        )

        assert response.status_code == 200
        db.session.refresh(media)
        assert (
            media.description
            == new_description[:MEDIA_DESCRIPTION_MAX_CHARACTERS]
        )

    def test_expected_scope_is_media_write(
        self, app: "Flask", user_1: "User"
    ) -> None:
        self.assert_response_scope(
            app=app,
            user=user_1,
            client_method="patch",
            endpoint=self.route.format(media_short_id=self.random_short_id()),
            invalid_scope="profile:read",
            expected_endpoint_scope="media:write",
        )


class TestMediaApiDelete(ApiTestCaseMixin, MediaMixin):
    route = "/api/media/{media_short_id}"

    def test_it_returns_401_when_user_is_not_authenticated(
        self, app: "Flask"
    ) -> None:
        client = app.test_client()

        response = client.delete(
            self.route.format(media_short_id=self.random_short_id())
        )

        self.assert_401(response)

    def test_it_returns_403_when_user_is_suspended(
        self, app: "Flask", suspended_user: "User"
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, suspended_user.email
        )

        response = client.delete(
            self.route.format(media_short_id=self.random_short_id()),
            headers={
                "Authorization": f"Bearer {auth_token}",
            },
        )

        self.assert_403(response)

    def test_it_returns_404_when_media_not_found(
        self, app: "Flask", user_1: "User"
    ) -> None:
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.delete(
            self.route.format(media_short_id=self.random_short_id()),
            headers={
                "Authorization": f"Bearer {auth_token}",
            },
        )

        self.assert_404_with_message(response, "media not found")

    def test_it_returns_403_when_user_is_not_media_owner(
        self, app: "Flask", user_1: "User", user_2: "User"
    ) -> None:
        media = self.create_media(user_2)
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.delete(
            self.route.format(media_short_id=media.short_id),
            headers={
                "Authorization": f"Bearer {auth_token}",
            },
        )
        self.assert_403(response)

    def test_it_deletes_user_media(
        self, app: "Flask", user_1: "User", user_2: "User"
    ) -> None:
        media_user_1 = self.create_media(user_1)
        media_user_2 = self.create_media(user_2)
        media_user_1_uuid = media_user_1.uuid
        client, auth_token = self.get_test_client_and_auth_token(
            app, user_1.email
        )

        response = client.delete(
            self.route.format(media_short_id=media_user_1.short_id),
            headers={
                "Authorization": f"Bearer {auth_token}",
            },
        )

        assert response.status_code == 204
        assert Media.query.filter_by(uuid=media_user_1_uuid).first() is None
        assert (
            Media.query.filter_by(uuid=media_user_2.uuid).first() is not None
        )

    def test_expected_scope_is_media_write(
        self, app: "Flask", user_1: "User"
    ) -> None:
        self.assert_response_scope(
            app=app,
            user=user_1,
            client_method="delete",
            endpoint=self.route.format(media_short_id=self.random_short_id()),
            invalid_scope="profile:read",
            expected_endpoint_scope="media:write",
        )
