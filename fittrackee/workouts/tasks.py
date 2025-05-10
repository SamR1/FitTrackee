import os
from datetime import datetime, timezone
from logging import Logger
from typing import Optional

from dramatiq.middleware import Shutdown, TimeLimitExceeded
from dramatiq_abort import Abort
from humanize import naturalsize

from fittrackee import db, dramatiq
from fittrackee.constants import TASKS_TIME_LIMIT, TaskPriority
from fittrackee.exceptions import TaskException
from fittrackee.users.models import Notification, UserTask
from fittrackee.utils import decode_short_id
from fittrackee.workouts.services.workouts_from_file_creation_service import (
    WorkoutsFromArchiveCreationAsyncService,
)

GENERIC_ERROR = "error during archive processing"
ABORT_ERROR = "task execution aborted"


def update_task_and_clean(
    *,
    error: str,
    upload_task: Optional["UserTask"] = None,
    upload_task_id: Optional[int] = None,
) -> None:
    if not upload_task and not upload_task_id:
        return
    if upload_task is None:
        upload_task = UserTask.query.filter_by(id=upload_task_id).first()
    if upload_task is None:
        return

    if error == ABORT_ERROR:
        upload_task.aborted = True
    else:
        upload_task.errored = True
        upload_task.errors = {
            **upload_task.errors,
            "archive": error,
        }
    db.session.commit()

    if (
        not upload_task.aborted
        and not Notification.query.filter_by(
            event_object_id=upload_task.id,
            event_type=upload_task.task_type,
        ).first()
    ):
        notification = Notification(
            from_user_id=upload_task.user_id,
            to_user_id=upload_task.user_id,
            created_at=datetime.now(tz=timezone.utc),
            event_object_id=upload_task.id,
            event_type=upload_task.task_type,
        )
        db.session.add(notification)
        db.session.commit()

    if upload_task.file_path and os.path.exists(upload_task.file_path):
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
    except (Abort, Shutdown, TimeLimitExceeded) as e:
        db.session.rollback()
        if isinstance(e, Abort):
            error = ABORT_ERROR
        elif isinstance(e, TimeLimitExceeded):
            error = "upload execution time exceeding limit"
        else:
            error = GENERIC_ERROR
        update_task_and_clean(error=error, upload_task_id=task_id)
        raise TaskException(error) from None
    except Exception as e:
        db.session.rollback()
        update_task_and_clean(error=GENERIC_ERROR, upload_task_id=task_id)
        raise TaskException(GENERIC_ERROR) from e
    finally:
        db.session.close()


def _handle_upload_task(upload_task: "UserTask", logger: "Logger") -> None:
    files_count = len(upload_task.data.get("files_to_process", []))
    file_size = str(upload_task.file_size) if upload_task.file_size else "0"
    logger.info(
        f"Processing task '{upload_task.short_id}' (files: {files_count}, "
        f"size: {naturalsize(file_size)})"
    )
    try:
        service = WorkoutsFromArchiveCreationAsyncService(upload_task.id)
        service.process()
        db.session.refresh(upload_task)
        archive_error = upload_task.errors.get("archive")
        if archive_error:
            logger.info(f" > archive error: {archive_error}")
        files_error = upload_task.errors.get("files", {})
        if files_error:
            logger.info(f" > errored files: {len(files_error.keys())}")
    except (KeyboardInterrupt, Exception) as e:
        db.session.rollback()
        error = (
            ABORT_ERROR if isinstance(e, KeyboardInterrupt) else GENERIC_ERROR
        )
        update_task_and_clean(error=error, upload_task_id=upload_task.id)
        raise e


def process_workouts_archives_uploads(max_count: int, logger: Logger) -> int:
    count = 0
    upload_tasks = (
        db.session.query(UserTask)
        .filter(
            UserTask.progress == 0,
            UserTask.errored == False,  # noqa
            UserTask.aborted == False,  # noqa
            UserTask.task_type == "workouts_archive_upload",
        )
        .order_by(UserTask.created_at)
        .limit(max_count)
        .all()
    )

    for upload_task in upload_tasks:
        _handle_upload_task(upload_task, logger)
        count += 1
        logger.info(" > done.")

    return count


def process_workouts_archive_upload(
    task_short_id: str, logger: Logger
) -> None:
    try:
        task_id = decode_short_id(task_short_id)
    except Exception as e:
        raise TaskException("Invalid task id") from e

    upload_task = UserTask.query.filter_by(
        uuid=task_id, task_type="workouts_archive_upload"
    ).first()
    if not upload_task:
        raise TaskException("No task found")
    if upload_task.progress > 0 or upload_task.errored or upload_task.aborted:
        raise TaskException("Task is not queued")

    _handle_upload_task(upload_task, logger)
