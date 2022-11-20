import pytest

from fittrackee.privacy_levels import PrivacyLevel, get_map_visibility


class TestMapVisibility:
    @pytest.mark.parametrize(
        'input_map_visibility',
        [
            PrivacyLevel.PUBLIC,
            PrivacyLevel.FOLLOWERS_AND_REMOTE,
            PrivacyLevel.FOLLOWERS,
            PrivacyLevel.PRIVATE,
        ],
    )
    def test_it_returns_map_visibility_when_workout_visibility_is_public(
        self,
        input_map_visibility: PrivacyLevel,
    ) -> None:
        assert (
            get_map_visibility(input_map_visibility, PrivacyLevel.PUBLIC)
            == input_map_visibility
        )

    @pytest.mark.parametrize(
        'input_map_visibility, expected_map_visibility',
        [
            (PrivacyLevel.PUBLIC, PrivacyLevel.FOLLOWERS_AND_REMOTE),
            (
                PrivacyLevel.FOLLOWERS_AND_REMOTE,
                PrivacyLevel.FOLLOWERS_AND_REMOTE,
            ),
            (PrivacyLevel.FOLLOWERS, PrivacyLevel.FOLLOWERS),
            (PrivacyLevel.PRIVATE, PrivacyLevel.PRIVATE),
        ],
    )
    def test_it_returns_map_visibility_when_workout_visibility_is_followers_only(  # noqa
        self,
        input_map_visibility: PrivacyLevel,
        expected_map_visibility: PrivacyLevel,
    ) -> None:
        assert (
            get_map_visibility(
                input_map_visibility, PrivacyLevel.FOLLOWERS_AND_REMOTE
            )
            == expected_map_visibility
        )

    @pytest.mark.parametrize(
        'input_map_visibility, expected_map_visibility',
        [
            (PrivacyLevel.PUBLIC, PrivacyLevel.FOLLOWERS),
            (
                PrivacyLevel.FOLLOWERS_AND_REMOTE,
                PrivacyLevel.FOLLOWERS,
            ),
            (PrivacyLevel.FOLLOWERS, PrivacyLevel.FOLLOWERS),
            (PrivacyLevel.PRIVATE, PrivacyLevel.PRIVATE),
        ],
    )
    def test_it_returns_map_visibility_when_workout_visibility_is_local_followers_only(  # noqa
        self,
        input_map_visibility: PrivacyLevel,
        expected_map_visibility: PrivacyLevel,
    ) -> None:
        assert (
            get_map_visibility(input_map_visibility, PrivacyLevel.FOLLOWERS)
            == expected_map_visibility
        )

    @pytest.mark.parametrize(
        'input_map_visibility',
        [
            PrivacyLevel.PUBLIC,
            PrivacyLevel.FOLLOWERS_AND_REMOTE,
            PrivacyLevel.FOLLOWERS,
            PrivacyLevel.PRIVATE,
        ],
    )
    def test_it_returns_map_visibility_when_workout_visibility_is_private(
        self,
        input_map_visibility: PrivacyLevel,
    ) -> None:
        assert (
            get_map_visibility(input_map_visibility, PrivacyLevel.PRIVATE)
            == PrivacyLevel.PRIVATE
        )
