import os

from dramatiq.middleware import Shutdown, TimeLimitExceeded

from fittrackee import db, dramatiq
from fittrackee.constants import TASKS_TIME_LIMIT, TaskPriority
from fittrackee.exceptions import TaskException
from fittrackee.files import get_absolute_file_path
from fittrackee.users.export_data import export_user_data
from fittrackee.users.models import UserTask


def update_task_and_clean(task_id: int) -> None:
    export_request = UserTask.query.filter_by(id=task_id).first()
    if not export_request:
        return

    export_request.errored = True
    export_directory = get_absolute_file_path(
        os.path.join("exports", str(export_request.user_id))
    )
    files = [
        f"user_{name}data.json"
        for name in ["", "workouts_", "equipments_", "comments_"]
    ]
    if export_request.file_path:
        files.append(export_request.file_path)
    for file in files:
        try:
            os.remove(os.path.join(export_directory, file))
        except OSError:
            continue
    db.session.commit()


@dramatiq.actor(
    queue_name="fittrackee_users_exports",
    priority=TaskPriority.MEDIUM,
    time_limit=TASKS_TIME_LIMIT,
    max_retries=0,
    notify_shutdown=True,
)
def export_data(task_id: int) -> None:
    try:
        export_user_data(task_id)
    except (Shutdown, TimeLimitExceeded) as e:
        update_task_and_clean(task_id)
        raise TaskException(
            "upload execution time exceeding limit"
            if isinstance(e, TimeLimitExceeded)
            else "worker shutdown during user data export"
        ) from None
    except Exception as e:
        update_task_and_clean(task_id)
        raise TaskException("error during user data export") from e
    finally:
        db.session.close()
