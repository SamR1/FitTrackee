import pytest
from flask import Flask

from fittrackee.users.models import FollowRequest, User
from fittrackee.visibility_levels import VisibilityLevel, can_view
from fittrackee.workouts.models import Sport, Workout

from .mixins import CommentMixin


class TestCanViewComment(CommentMixin):
    @pytest.mark.parametrize(
        "input_description,input_text_visibility",
        [
            (
                f"comment visibility: {VisibilityLevel.PRIVATE.value}",
                VisibilityLevel.PRIVATE,
            ),
            (
                f"comment visibility: {VisibilityLevel.FOLLOWERS.value}",
                VisibilityLevel.FOLLOWERS,
            ),
            (
                f"comment visibility: {VisibilityLevel.PUBLIC.value}",
                VisibilityLevel.PUBLIC,
            ),
        ],
    )
    def test_comment_owner_can_view_his_comment(
        self,
        input_description: str,
        input_text_visibility: VisibilityLevel,
        app: Flask,
        user_1: User,
        sport_1_cycling: Sport,
        workout_cycling_user_1: Workout,
    ) -> None:
        workout_cycling_user_1.workout_visibility = VisibilityLevel.PUBLIC
        comment = self.create_comment(
            user_1,
            workout_cycling_user_1,
            text_visibility=input_text_visibility,
        )

        assert can_view(comment, "text_visibility", user_1) is True

    def test_follower_can_not_view_comment_when_private(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        follow_request_from_user_1_to_user_2: FollowRequest,
    ) -> None:
        user_2.approves_follow_request_from(user_1)
        workout_cycling_user_2.workout_visibility = VisibilityLevel.PUBLIC
        comment = self.create_comment(
            user_2,
            workout_cycling_user_2,
            text_visibility=VisibilityLevel.PRIVATE,
        )

        assert can_view(comment, "text_visibility", user_1) is False

    @pytest.mark.parametrize(
        "input_description,input_text_visibility",
        [
            (
                f"comment visibility: {VisibilityLevel.FOLLOWERS.value}",
                VisibilityLevel.FOLLOWERS,
            ),
            (
                f"comment visibility: {VisibilityLevel.PUBLIC.value}",
                VisibilityLevel.PUBLIC,
            ),
        ],
    )
    def test_follower_can_view_comment_when_public_or_follower_only(
        self,
        input_description: str,
        input_text_visibility: VisibilityLevel,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
        follow_request_from_user_1_to_user_2: FollowRequest,
    ) -> None:
        user_2.approves_follow_request_from(user_1)
        workout_cycling_user_2.workout_visibility = VisibilityLevel.PUBLIC
        comment = self.create_comment(
            user_2,
            workout_cycling_user_2,
            text_visibility=input_text_visibility,
        )

        assert can_view(comment, "text_visibility", user_1) is True

    @pytest.mark.parametrize(
        "input_description,input_text_visibility",
        [
            (
                f"comment visibility: {VisibilityLevel.PRIVATE.value}",
                VisibilityLevel.PRIVATE,
            ),
            (
                f"comment visibility: {VisibilityLevel.FOLLOWERS.value}",
                VisibilityLevel.FOLLOWERS,
            ),
        ],
    )
    def test_another_user_can_not_view_comment_when_private_or_follower_only(
        self,
        input_description: str,
        input_text_visibility: VisibilityLevel,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        workout_cycling_user_2.workout_visibility = VisibilityLevel.PUBLIC
        comment = self.create_comment(
            user_2,
            workout_cycling_user_2,
            text_visibility=input_text_visibility,
        )

        assert can_view(comment, "text_visibility", user_1) is False

    def test_another_user_can_view_comment_when_private_and_user_mentioned(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        workout_cycling_user_2.workout_visibility = VisibilityLevel.PUBLIC
        comment = self.create_comment(
            user_2,
            workout_cycling_user_2,
            text=f"@{user_1.username}",
            text_visibility=VisibilityLevel.PRIVATE,
        )

        assert can_view(comment, "text_visibility", user_1) is True

    def test_another_user_can_view_comment_when_public(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        workout_cycling_user_2.workout_visibility = VisibilityLevel.PUBLIC
        comment = self.create_comment(
            user_2,
            workout_cycling_user_2,
            text_visibility=VisibilityLevel.PUBLIC,
        )

        assert can_view(comment, "text_visibility", user_1) is True

    def test_another_user_can_not_view_comment_when_public_and_user_blocked(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        workout_cycling_user_2.workout_visibility = VisibilityLevel.PUBLIC
        comment = self.create_comment(
            user_2,
            workout_cycling_user_2,
            text_visibility=VisibilityLevel.PUBLIC,
        )
        user_2.blocks_user(user_1)

        assert can_view(comment, "text_visibility", user_1) is False

    @pytest.mark.parametrize(
        "input_description,input_text_visibility",
        [
            (
                f"comment visibility: {VisibilityLevel.PRIVATE.value}",
                VisibilityLevel.PRIVATE,
            ),
            (
                f"comment visibility: {VisibilityLevel.FOLLOWERS.value}",
                VisibilityLevel.FOLLOWERS,
            ),
        ],
    )
    def test_comment_can_not_viewed_when_no_user_and_private_or_follower_only_visibility(  # noqa
        self,
        input_description: str,
        input_text_visibility: VisibilityLevel,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        workout_cycling_user_2.workout_visibility = VisibilityLevel.PUBLIC
        comment = self.create_comment(
            user_2,
            workout_cycling_user_2,
            text_visibility=input_text_visibility,
        )

        assert can_view(comment, "text_visibility") is False

    def test_comment_can_be_viewed_when_public_and_no_user_provided(
        self,
        app: Flask,
        user_1: User,
        user_2: User,
        sport_1_cycling: Sport,
        workout_cycling_user_2: Workout,
    ) -> None:
        workout_cycling_user_2.workout_visibility = VisibilityLevel.PUBLIC
        comment = self.create_comment(
            user_2,
            workout_cycling_user_2,
            text_visibility=VisibilityLevel.PUBLIC,
        )

        assert can_view(comment, "text_visibility") is True
