from enum import Enum


class ActivityType(Enum):
    FOLLOW = 'Follow'


class ActorType(Enum):
    APPLICATION = 'Application'
    GROUP = 'Group'
    PERSON = 'Person'
