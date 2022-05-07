from enum import Enum


class ActivityType(Enum):
    ACCEPT = 'Accept'
    CREATE = 'Create'
    FOLLOW = 'Follow'
    REJECT = 'Reject'
    UNDO = 'Undo'


class ActorType(Enum):
    APPLICATION = 'Application'
    GROUP = 'Group'
    PERSON = 'Person'
