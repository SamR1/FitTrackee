import os

from dramatiq.middleware import Shutdown, TimeLimitExceeded

from fittrackee import db, dramatiq
from fittrackee.constants import TASKS_TIME_LIMIT, TaskPriority
from fittrackee.exceptions import TaskException
from fittrackee.users.models import UserTask
from fittrackee.workouts.services.workouts_from_file_creation_service import (
    WorkoutsFromArchiveCreationAsyncService,
)

GENERIC_ERROR = "error during archive processing"


def update_task_and_clean(task_id: int, error: str) -> None:
    upload_task = UserTask.query.filter_by(id=task_id).first()
    if not upload_task:
        return
    upload_task.errored = True
    upload_task.errors = {
        **upload_task.errors,
        "archive": error,
    }
    db.session.commit()
    if os.path.exists(upload_task.file_path):
        os.remove(upload_task.file_path)


@dramatiq.actor(
    queue_name="fittrackee_workouts",
    priority=TaskPriority.MEDIUM,
    time_limit=TASKS_TIME_LIMIT,
    max_retries=0,
    notify_shutdown=True,
)
def upload_workouts_archive(task_id: int) -> None:
    try:
        service = WorkoutsFromArchiveCreationAsyncService(task_id)
        service.process()
    except (Shutdown, TimeLimitExceeded) as e:
        db.session.rollback()
        error = (
            "upload execution time exceeding limit"
            if isinstance(e, TimeLimitExceeded)
            else GENERIC_ERROR
        )
        update_task_and_clean(task_id, error)
        raise TaskException(error) from None
    except Exception as e:
        db.session.rollback()
        update_task_and_clean(task_id, GENERIC_ERROR)
        raise TaskException(GENERIC_ERROR) from e
    finally:
        db.session.close()
