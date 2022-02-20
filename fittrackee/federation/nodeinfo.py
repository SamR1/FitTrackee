from flask import Blueprint, current_app

from fittrackee.federation.models import Actor
from fittrackee.responses import HttpResponse
from fittrackee.workouts.models import Workout

from .decorators import federation_required
from .models import Domain

ap_nodeinfo_blueprint = Blueprint('ap_nodeinfo', __name__)


@ap_nodeinfo_blueprint.route('/.well-known/nodeinfo', methods=['GET'])
@federation_required
def get_nodeinfo_url(app_domain: Domain) -> HttpResponse:
    """
    Get node info links

    **Example request**:

    .. sourcecode:: http

      GET /.well-known/nodeinfo HTTP/1.1
      Content-Type: application/json

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json; charset=utf-8

      {
        "links": [
          {
            "rel": "http://nodeinfo.diaspora.software/ns/schema/2.0",
            "href": "https://example.com/nodeinfo/2.0"
          }
        ]
      }

    :statuscode 200: success
    :statuscode 403: error, federation is disabled for this instance

    """
    nodeinfo_url = f'https://{app_domain.name}/nodeinfo/2.0'
    response = {
        'links': [
            {
                'rel': 'http://nodeinfo.diaspora.software/ns/schema/2.0',
                'href': nodeinfo_url,
            }
        ]
    }
    return HttpResponse(
        response=response, content_type='application/json; charset=utf-8'
    )


@ap_nodeinfo_blueprint.route('/nodeinfo/2.0', methods=['GET'])
@federation_required
def get_nodeinfo(app_domain: Domain) -> HttpResponse:
    """
    Get node infos

    **Example request**:

    .. sourcecode:: http

      GET /nodeinfo/2.0 HTTP/1.1
      Content-Type: application/json

    **Example response**:

    .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json; charset=utf-8

      {
        "version": "2.0",
        "software": {
          "name": "fittrackee",
          "version": "0.5.7"
        },
        "protocols": [
          "activitypub"
        ],
        "usage": {
          "users": {
            "total": 10
          },
          "localWorkouts": 35
        },
        "openRegistrations": true
      }

    :statuscode 200: success
    :statuscode 403: error, federation is disabled for this instance

    """
    # TODO : add 'activeHalfyear' and 'activeMonth' for users
    workouts_count = Workout.query.filter().count()
    actor_count = Actor.query.filter_by(domain_id=app_domain.id).count()
    response = {
        'version': '2.0',
        'software': {
            'name': 'fittrackee',
            'version': current_app.config['VERSION'],
        },
        'protocols': ['activitypub'],
        'usage': {
            'users': {'total': actor_count},
            'localWorkouts': workouts_count,
        },
        'openRegistrations': current_app.config['is_registration_enabled'],
    }
    return HttpResponse(
        response=response, content_type='application/json; charset=utf-8'
    )
