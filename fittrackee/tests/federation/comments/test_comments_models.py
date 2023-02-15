from unittest.mock import Mock, patch

import pytest
from flask import Flask

from fittrackee.comments.exceptions import CommentForbiddenException
from fittrackee.comments.models import Mention
from fittrackee.exceptions import InvalidVisibilityException
from fittrackee.privacy_levels import PrivacyLevel
from fittrackee.users.models import FollowRequest, User
from fittrackee.workouts.models import Sport, Workout

from ...comments.utils import CommentMixin
from ...utils import RandomActor


class TestWorkoutCommentModelSerializeForCommentOwner(CommentMixin):
    def test_it_serializes_owner_comment(
        self,
        app_with_federation: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.workout_visibility = (
            PrivacyLevel.FOLLOWERS_AND_REMOTE
        )
        comment = self.create_comment(
            user=user_1,
            workout=workout_cycling_user_1,
            text_visibility=PrivacyLevel.FOLLOWERS_AND_REMOTE,
        )

        serialized_comment = comment.serialize(user_1)

        assert serialized_comment == {
            'id': comment.short_id,
            'user': user_1.serialize(),
            'workout_id': workout_cycling_user_1.short_id,
            'text': comment.text,
            'text_html': comment.text,  # no mention
            'text_visibility': comment.text_visibility,
            'created_at': comment.created_at,
            'modification_date': comment.modification_date,
            'reply_to': comment.reply_to,
            'replies': [],
        }


class TestWorkoutCommentModelSerializeForRemoteFollower(CommentMixin):
    def test_it_raises_error_when_user_does_not_follow_comment_user(
        self,
        app_with_federation: Flask,
        remote_user: User,
        sport_1_cycling: Sport,
        remote_cycling_workout: Workout,
        user_1: User,
    ) -> None:
        remote_cycling_workout.workout_visibility = (
            PrivacyLevel.FOLLOWERS_AND_REMOTE
        )
        comment = self.create_comment(
            user=remote_user,
            workout=remote_cycling_workout,
            text_visibility=PrivacyLevel.FOLLOWERS_AND_REMOTE,
        )

        with pytest.raises(CommentForbiddenException):
            comment.serialize(user_1)

    def test_it_raises_error_when_privacy_does_not_allows_it(
        self,
        app_with_federation: Flask,
        remote_user: User,
        sport_1_cycling: Sport,
        remote_cycling_workout: Workout,
        user_1: User,
        follow_request_from_user_1_to_remote_user: FollowRequest,
    ) -> None:
        remote_user.approves_follow_request_from(user_1)
        remote_cycling_workout.workout_visibility = (
            PrivacyLevel.FOLLOWERS_AND_REMOTE
        )
        comment = self.create_comment(
            user=remote_user,
            workout=remote_cycling_workout,
            text_visibility=PrivacyLevel.FOLLOWERS,
        )

        with pytest.raises(CommentForbiddenException):
            comment.serialize(user_1)

    @pytest.mark.parametrize(
        'input_visibility',
        [PrivacyLevel.FOLLOWERS_AND_REMOTE, PrivacyLevel.PUBLIC],
    )
    def test_it_serializes_comment_for_follower_when_privacy_allows_it(
        self,
        app_with_federation: Flask,
        user_1: User,
        remote_user: User,
        sport_1_cycling: Sport,
        remote_cycling_workout: Workout,
        follow_request_from_user_1_to_remote_user: FollowRequest,
        input_visibility: PrivacyLevel,
    ) -> None:
        remote_user.approves_follow_request_from(user_1)
        remote_cycling_workout.workout_visibility = input_visibility
        comment = self.create_comment(
            user=remote_user,
            workout=remote_cycling_workout,
            text_visibility=input_visibility,
        )

        serialized_comment = comment.serialize(user_1)

        assert serialized_comment == {
            'id': comment.short_id,
            'user': remote_user.serialize(),
            'workout_id': remote_cycling_workout.short_id,
            'text': comment.text,
            'text_html': comment.text,  # no mention
            'text_visibility': comment.text_visibility,
            'created_at': comment.created_at,
            'modification_date': comment.modification_date,
            'reply_to': comment.reply_to,
            'replies': [],
        }


class TestWorkoutCommentModelSerializeForUser(CommentMixin):
    def test_it_raises_error_when_comment_is_visible_to_remote_follower(
        self,
        app_with_federation: Flask,
        user_1: User,
        remote_user: User,
        sport_1_cycling: Sport,
        remote_cycling_workout: Workout,
    ) -> None:
        remote_cycling_workout.workout_visibility = PrivacyLevel.PUBLIC
        comment = self.create_comment(
            user=remote_user,
            workout=remote_cycling_workout,
            text_visibility=PrivacyLevel.FOLLOWERS_AND_REMOTE,
        )

        with pytest.raises(CommentForbiddenException):
            comment.serialize(user_1)


class TestWorkoutCommentModelSerializeForUnauthenticatedUser(CommentMixin):
    def test_it_raises_error_when_comment_is_visible_to_remote_follower(
        self,
        app_with_federation: Flask,
        user_1: User,
        remote_user: User,
        sport_1_cycling: Sport,
        remote_cycling_workout: Workout,
    ) -> None:
        remote_cycling_workout.workout_visibility = PrivacyLevel.PUBLIC
        comment = self.create_comment(
            user=user_1,
            workout=remote_cycling_workout,
            text_visibility=PrivacyLevel.FOLLOWERS_AND_REMOTE,
        )

        with pytest.raises(CommentForbiddenException):
            comment.serialize()


class TestWorkoutCommentModelGetCreateActivity(CommentMixin):
    activity_type = 'Create'
    expected_object_type = 'Note'

    @pytest.mark.parametrize(
        'input_visibility', [PrivacyLevel.PRIVATE, PrivacyLevel.FOLLOWERS]
    )
    def test_it_raises_error_if_visibility_is_invalid(
        self,
        app_with_federation: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        remote_cycling_workout: Workout,
        input_visibility: PrivacyLevel,
    ) -> None:
        remote_cycling_workout.workout_visibility = PrivacyLevel.PUBLIC
        comment = self.create_comment(
            user=user_1,
            workout=remote_cycling_workout,
            text_visibility=input_visibility,
        )
        with pytest.raises(InvalidVisibilityException):
            comment.get_activity(activity_type=self.activity_type)

    @pytest.mark.parametrize(
        'input_visibility',
        [PrivacyLevel.FOLLOWERS_AND_REMOTE, PrivacyLevel.PUBLIC],
    )
    def test_it_returns_activities_when_visibility_is_valid(
        self,
        app_with_federation: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        remote_cycling_workout: Workout,
        input_visibility: PrivacyLevel,
    ) -> None:
        remote_cycling_workout.workout_visibility = PrivacyLevel.PUBLIC
        comment = self.create_comment(
            user=user_1,
            workout=remote_cycling_workout,
            text_visibility=input_visibility,
        )

        note_activity = comment.get_activity(activity_type=self.activity_type)

        assert note_activity['type'] == self.activity_type
        assert note_activity['object']['type'] == self.expected_object_type
        assert note_activity['object']['id'] == comment.ap_id


class TestWorkoutCommentModelGetDeleteActivity(
    TestWorkoutCommentModelGetCreateActivity
):
    activity_type = 'Delete'
    expected_object_type = 'Tombstone'


@patch('fittrackee.federation.utils.user.update_remote_user')
class TestWorkoutCommentModelWithMentions(CommentMixin):
    def test_it_creates_mentions_when_mentioned_user_exists(
        self,
        update_mock: Mock,
        app_with_federation: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        user_2: User,
        remote_user: User,
    ) -> None:
        workout_cycling_user_1.workout_visibility = PrivacyLevel.PUBLIC
        comment = self.create_comment(
            user=user_2,
            workout=workout_cycling_user_1,
            text=f"@{remote_user.fullname} {self.random_string()}",
            text_visibility=PrivacyLevel.PUBLIC,
            with_mentions=False,
        )

        comment.create_mentions()

        mention = Mention.query.first()
        assert mention.comment_id == comment.id
        assert mention.user_id == remote_user.id

    def test_it_creates_mentions_when_mentioned_user_does_not_exist(
        self,
        update_mock: Mock,
        app_with_federation: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        user_2: User,
        random_actor: RandomActor,
    ) -> None:
        workout_cycling_user_1.workout_visibility = PrivacyLevel.PUBLIC
        comment = self.create_comment(
            user=user_2,
            workout=workout_cycling_user_1,
            text=f"@{random_actor.fullname} {self.random_string()}",
            text_visibility=PrivacyLevel.PUBLIC,
            with_mentions=False,
        )

        with patch(
            'fittrackee.federation.utils.user.fetch_account_from_webfinger',
            return_value=random_actor.get_webfinger(),
        ), patch(
            'fittrackee.federation.utils.user.get_remote_actor_url',
            return_value=random_actor.get_remote_user_object(),
        ):
            comment.create_mentions()

        remote_user = User.query.filter_by(username=random_actor.name).first()
        mention = Mention.query.first()
        assert mention.comment_id == comment.id
        assert mention.user_id == remote_user.id

    def test_it_returns_mentioned_user(
        self,
        update_mock: Mock,
        app_with_federation: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        user_2: User,
        remote_user: User,
    ) -> None:
        workout_cycling_user_1.workout_visibility = PrivacyLevel.PUBLIC
        mention = f"@{remote_user.fullname}"
        comment = self.create_comment(
            user=user_2,
            workout=workout_cycling_user_1,
            text=f"{mention} {self.random_string()}",
            text_visibility=PrivacyLevel.PUBLIC,
            with_mentions=False,
        )

        _, mentioned_users = comment.create_mentions()

        assert mentioned_users == {"local": set(), "remote": {remote_user}}


@patch('fittrackee.federation.utils.user.update_remote_user')
class TestWorkoutCommentModelSerializeForMentions(CommentMixin):
    def test_it_serializes_comment_with_mentions_as_link(
        self,
        update_mock: Mock,
        app_with_federation: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
        user_2: User,
        remote_user: User,
    ) -> None:
        workout_cycling_user_1.workout_visibility = PrivacyLevel.PUBLIC
        comment = self.create_comment(
            user=user_2,
            workout=workout_cycling_user_1,
            text=f"@{remote_user.fullname} {self.random_string()}",
            text_visibility=PrivacyLevel.PUBLIC,
        )

        serialized_comment = comment.serialize(user_1)

        assert serialized_comment["text"] == comment.text
        assert serialized_comment["text_html"] == comment.handle_mentions()[0]
