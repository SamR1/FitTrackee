from enum import Enum


class ActivityType(Enum):
    ACCEPT = 'Accept'
    FOLLOW = 'Follow'
    REJECT = 'Reject'


class ActorType(Enum):
    APPLICATION = 'Application'
    GROUP = 'Group'
    PERSON = 'Person'
