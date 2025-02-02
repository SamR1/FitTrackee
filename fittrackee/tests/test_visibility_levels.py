import pytest

from fittrackee.visibility_levels import (
    VisibilityLevel,
    get_calculated_visibility,
)


class TestMapVisibility:
    @pytest.mark.parametrize(
        "input_visibility",
        [
            VisibilityLevel.PUBLIC,
            VisibilityLevel.FOLLOWERS,
            VisibilityLevel.PRIVATE,
        ],
    )
    def test_it_returns_visibility_when_parent_visibility_is_public(
        self,
        input_visibility: VisibilityLevel,
    ) -> None:
        assert (
            get_calculated_visibility(
                visibility=input_visibility,
                parent_visibility=VisibilityLevel.PUBLIC,
            )
            == input_visibility
        )

    @pytest.mark.parametrize(
        "input_visibility, expected_visibility",
        [
            (VisibilityLevel.PUBLIC, VisibilityLevel.FOLLOWERS),
            (VisibilityLevel.FOLLOWERS, VisibilityLevel.FOLLOWERS),
            (VisibilityLevel.PRIVATE, VisibilityLevel.PRIVATE),
        ],
    )
    def test_it_returns_map_visibility_when_analysis_visibility_is_followers_only(  # noqa
        self,
        input_visibility: VisibilityLevel,
        expected_visibility: VisibilityLevel,
    ) -> None:
        assert (
            get_calculated_visibility(
                visibility=input_visibility,
                parent_visibility=VisibilityLevel.FOLLOWERS,
            )
            == expected_visibility
        )

    @pytest.mark.parametrize(
        "input_visibility",
        [
            VisibilityLevel.PUBLIC,
            VisibilityLevel.FOLLOWERS,
            VisibilityLevel.PRIVATE,
        ],
    )
    def test_it_returns_visibility_when_parent_visibility_is_private(
        self,
        input_visibility: VisibilityLevel,
    ) -> None:
        assert (
            get_calculated_visibility(
                visibility=input_visibility,
                parent_visibility=VisibilityLevel.PRIVATE,
            )
            == VisibilityLevel.PRIVATE
        )
