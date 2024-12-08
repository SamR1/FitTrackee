import pytest

from fittrackee.visibility_levels import VisibilityLevel, get_map_visibility


class TestMapVisibility:
    @pytest.mark.parametrize(
        'input_map_visibility',
        [
            VisibilityLevel.PUBLIC,
            VisibilityLevel.FOLLOWERS,
            VisibilityLevel.PRIVATE,
        ],
    )
    def test_it_returns_map_visibility_when_workout_visibility_is_public(
        self,
        input_map_visibility: VisibilityLevel,
    ) -> None:
        assert (
            get_map_visibility(input_map_visibility, VisibilityLevel.PUBLIC)
            == input_map_visibility
        )

    @pytest.mark.parametrize(
        'input_map_visibility, expected_map_visibility',
        [
            (VisibilityLevel.PUBLIC, VisibilityLevel.FOLLOWERS),
            (VisibilityLevel.FOLLOWERS, VisibilityLevel.FOLLOWERS),
            (VisibilityLevel.PRIVATE, VisibilityLevel.PRIVATE),
        ],
    )
    def test_it_returns_map_visibility_when_workout_visibility_is_followers_only(  # noqa
        self,
        input_map_visibility: VisibilityLevel,
        expected_map_visibility: VisibilityLevel,
    ) -> None:
        assert (
            get_map_visibility(input_map_visibility, VisibilityLevel.FOLLOWERS)
            == expected_map_visibility
        )

    @pytest.mark.parametrize(
        'input_map_visibility',
        [
            VisibilityLevel.PUBLIC,
            VisibilityLevel.FOLLOWERS,
            VisibilityLevel.PRIVATE,
        ],
    )
    def test_it_returns_map_visibility_when_workout_visibility_is_private(
        self,
        input_map_visibility: VisibilityLevel,
    ) -> None:
        assert (
            get_map_visibility(input_map_visibility, VisibilityLevel.PRIVATE)
            == VisibilityLevel.PRIVATE
        )
