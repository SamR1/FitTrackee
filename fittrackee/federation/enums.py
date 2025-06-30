from enum import Enum


class ActivityType(Enum):
    ACCEPT = "Accept"
    CREATE = "Create"
    DELETE = "Delete"
    FOLLOW = "Follow"
    LIKE = "Like"
    REJECT = "Reject"
    UNDO = "Undo"
    UPDATE = "Update"


class ActorType(Enum):
    APPLICATION = "Application"
    GROUP = "Group"
    PERSON = "Person"
