from enum import Enum


class PrivacyLevel(str, Enum):  # to make enum serializable
    PUBLIC = 'public'
    FOLLOWERS_AND_REMOTE = 'followers_and_remote_only'
    FOLLOWERS = 'followers_only'  # only local followers in federated instances
    PRIVATE = 'private'


def get_map_visibility(
    map_visibility: PrivacyLevel, workout_visibility: PrivacyLevel
) -> PrivacyLevel:
    # workout privacy overrides map privacy, when stricter
    if (
        workout_visibility == PrivacyLevel.PRIVATE
        or (
            workout_visibility == PrivacyLevel.FOLLOWERS
            and map_visibility
            in [PrivacyLevel.FOLLOWERS_AND_REMOTE, PrivacyLevel.PUBLIC]
        )
        or (
            workout_visibility == PrivacyLevel.FOLLOWERS_AND_REMOTE
            and map_visibility == PrivacyLevel.PUBLIC
        )
    ):
        return workout_visibility
    return map_visibility
