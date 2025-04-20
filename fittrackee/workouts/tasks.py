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
from fittrackee.workouts.services.workouts_from_file_creation_service import (
    WorkoutsFromArchiveCreationAsyncService,
)

GENERIC_ERROR = "error during archive processing"


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

    if error == "task execution aborted":
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
    except (Shutdown, TimeLimitExceeded) as e:
        db.session.rollback()
        error = (
            "upload execution time exceeding limit"
            if isinstance(e, TimeLimitExceeded)
            else GENERIC_ERROR
        )
        update_task_and_clean(error=error, upload_task_id=task_id)
        raise TaskException(error) from None
    except Abort:
        db.session.rollback()
        error = "task execution aborted"
        update_task_and_clean(error=error, upload_task_id=task_id)
        raise TaskException(error) from None
    except Exception as e:
        db.session.rollback()
        update_task_and_clean(error=GENERIC_ERROR, upload_task_id=task_id)
        raise TaskException(GENERIC_ERROR) from e
    finally:
        db.session.close()


def process_workouts_archives_upload(max_count: int, logger: Logger) -> int:
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
        files_count = len(upload_task.data.get("files_to_process", []))
        file_size = (
            str(upload_task.file_size) if upload_task.file_size else "0"
        )
        logger.info(
            f"Processing task '{upload_task.id}' (files: {files_count}, "
            f"size: {naturalsize(file_size)})..."
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
            count += 1
        except (KeyboardInterrupt, Exception) as e:
            db.session.rollback()
            error = (
                "task execution aborted"
                if isinstance(e, KeyboardInterrupt)
                else GENERIC_ERROR
            )
            update_task_and_clean(error=error, upload_task_id=upload_task.id)
            raise e

    return count
