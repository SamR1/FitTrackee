from fittrackee import dramatiq
from fittrackee.workouts.services.workouts_from_file_creation_service import (
    WorkoutsFromArchiveCreationAsyncService,
)


@dramatiq.actor(queue_name="fittrackee_workouts")
def upload_workouts_archive(task_id: int) -> None:
    service = WorkoutsFromArchiveCreationAsyncService(task_id)
    service.process()
