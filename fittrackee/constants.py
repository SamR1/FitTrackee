import os
from enum import IntEnum

TASKS_TIME_LIMIT = int(os.environ.get("TASKS_TIME_LIMIT", "1800")) * 1000


class TaskPriority(IntEnum):
    LOW = 100
    MEDIUM = 50
    HIGH = 0
