from fittrackee import appLog, db, dramatiq
from fittrackee.federation.models import Domain
from fittrackee.federation.utils.remote_domain import (
    get_remote_server_node_info_data,
    get_remote_server_node_info_url,
)


@dramatiq.actor(queue_name='fittrackee_remote_server')
def update_remote_server(domain_name: str) -> None:
    try:
        node_info_url = get_remote_server_node_info_url(domain_name)
        node_info_data = get_remote_server_node_info_data(node_info_url)

        domain = Domain.query.filter_by(name=domain_name).first()
        domain.software_name = node_info_data.get('software', {}).get('name')
        domain.software_version = node_info_data.get('software', {}).get(
            'version'
        )

        db.session.commit()
    except Exception as e:
        appLog.error(f"Error when updating remote server '{domain_name}': {e}")
