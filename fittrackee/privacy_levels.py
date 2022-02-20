from enum import Enum


class PrivacyLevel(Enum):
    PUBLIC = 'public'
    FOLLOWERS = 'followers_only'
    PRIVATE = 'private'


def get_map_visibility(
    map_visibility: PrivacyLevel, workout_visibility: PrivacyLevel
) -> PrivacyLevel:
    # workout privacy overrides map privacy, when stricter
    if workout_visibility == PrivacyLevel.PRIVATE or (
        workout_visibility == PrivacyLevel.FOLLOWERS
        and map_visibility == PrivacyLevel.PUBLIC
    ):
        return workout_visibility
    return map_visibility
