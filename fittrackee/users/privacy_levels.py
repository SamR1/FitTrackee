from enum import Enum


class PrivacyLevel(Enum):
    PUBLIC = 'public'
    FOLLOWERS = 'followers_only'
    PRIVATE = 'private'
