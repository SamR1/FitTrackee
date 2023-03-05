from fittrackee import dramatiq
from fittrackee.users.export_data import export_user_data


@dramatiq.actor(queue_name='fittrackee_users_exports')
def export_data(export_request_id: int) -> None:
    export_user_data(export_request_id)
