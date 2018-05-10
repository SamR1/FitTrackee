import json
import os

from flask import Blueprint, jsonify, request
from mpwo_api import appLog, db
from sqlalchemy import exc

from ..users.utils import authenticate, verify_extension
from .models import Activity
from .utils import (
    create_activity, edit_activity_wo_gpx, get_file_path, get_gpx_info
)

activities_blueprint = Blueprint('activities', __name__)


@activities_blueprint.route('/activities', methods=['GET'])
@authenticate
def get_activities(auth_user_id):
    """Get all activities for authenticated user"""
    activities = Activity.query.filter_by(user_id=auth_user_id)\
        .order_by(Activity.activity_date.desc()).all()
    activities_list = []
    for activity in activities:
        activities_list.append(activity.serialize())
    response_object = {
        'status': 'success',
        'data': {
            'activities': activities_list
        }
    }
    return jsonify(response_object), 200


@activities_blueprint.route('/activities/<int:activity_id>', methods=['GET'])
@authenticate
def get_activity(auth_user_id, activity_id):
    """Get an activity"""
    activity = Activity.query.filter_by(id=activity_id).first()
    activities_list = []

    if activity:
        activities_list.append(activity.serialize())
        status = 'success'
        code = 200
    else:
        status = 'not found'
        code = 404

    response_object = {
        'status': status,
        'data': {
            'activities': activities_list
        }
    }
    return jsonify(response_object), code


@activities_blueprint.route(
    '/activities/<int:activity_id>/gpx', methods=['GET']
)
@authenticate
def get_activity_gpx(auth_user_id, activity_id):
    """Get gpx file for an activity"""
    activity = Activity.query.filter_by(id=activity_id).first()
    if activity:
        if not activity.gpx or activity.gpx == '':
            response_object = {
                'status': 'fail',
                'message': 'No gpx file for this activity (id: {})'.format(
                    activity_id
                )
            }
            return jsonify(response_object), 400

        try:
            with open(activity.gpx, encoding='utf-8') as f:
                gpx_content = f.read()
        except Exception as e:
            appLog.error(e)
            response_object = {
                'status': 'error',
                'message': 'internal error',
                'data': {
                    'gpx': ''
                }
            }
            return jsonify(response_object), 500

        status = 'success'
        message = ''
        code = 200
    else:
        gpx_content = ''
        status = 'not found'
        message = 'Activity not found (id: {})'.format(activity_id)
        code = 404

    response_object = {
        'status': status,
        'message': message,
        'data': {
            'gpx': gpx_content
        }
    }
    return jsonify(response_object), code


@activities_blueprint.route('/activities', methods=['POST'])
@authenticate
def post_activity(auth_user_id):
    """Post an activity"""
    response_object = verify_extension('activity', request)
    if response_object['status'] != 'success':
        return jsonify(response_object), 400

    activity_data = json.loads(request.form["data"])
    if not activity_data or activity_data.get('sport_id') is None:
        response_object = {
            'status': 'error',
            'message': 'Invalid payload.'
        }
        return jsonify(response_object), 400

    activity_file = request.files['file']
    file_path = get_file_path(auth_user_id, activity_file)

    try:
        activity_file.save(file_path)
        gpx_data = get_gpx_info(file_path)
    except Exception as e:
        appLog.error(e)
        response_object = {
            'status': 'error',
            'message': 'Error during activity file save.'
        }
        return jsonify(response_object), 500

    try:
        new_activity = create_activity(
            auth_user_id, activity_data, gpx_data, file_path)
        db.session.add(new_activity)
        db.session.commit()
        response_object = {
            'status': 'created',
            'data': {
                'activities': [new_activity.serialize()]
            }
        }
        return jsonify(response_object), 201

    except (exc.IntegrityError, ValueError) as e:
        db.session.rollback()
        appLog.error(e)
        response_object = {
            'status': 'fail',
            'message': 'Error during activity save.'
        }
        return jsonify(response_object), 500


@activities_blueprint.route('/activities/no_gpx', methods=['POST'])
@authenticate
def post_activity_no_gpx(auth_user_id):
    """Post an activity without gpx file"""
    activity_data = request.get_json()
    if not activity_data or activity_data.get('sport_id') is None \
            or activity_data.get('duration') is None \
            or activity_data.get('distance') is None \
            or activity_data.get('activity_date') is None:
        response_object = {
            'status': 'error',
            'message': 'Invalid payload.'
        }
        return jsonify(response_object), 400

    try:
        new_activity = create_activity(auth_user_id, activity_data)
        db.session.add(new_activity)
        db.session.commit()

        response_object = {
            'status': 'created',
            'data': {
                'activities': [new_activity.serialize()]
            }
        }
        return jsonify(response_object), 201

    except (exc.IntegrityError, ValueError) as e:
        db.session.rollback()
        appLog.error(e)
        response_object = {
            'status': 'fail',
            'message': 'Error during activity save.'
        }
        return jsonify(response_object), 500


@activities_blueprint.route('/activities/<int:activity_id>', methods=['PATCH'])
@authenticate
def update_activity(auth_user_id, activity_id):
    """Update an activity"""
    activity_data = request.get_json()
    if not activity_data or activity_data.get('sport_id') is None \
            or activity_data.get('duration') is None \
            or activity_data.get('distance') is None \
            or activity_data.get('activity_date') is None:
        response_object = {
            'status': 'error',
            'message': 'Invalid payload.'
        }
        return jsonify(response_object), 400

    try:
        activity = Activity.query.filter_by(id=activity_id).first()
        if activity:
            if activity.gpx:
                response_object = {
                    'status': 'error',
                    'message': 'You can not modify an activity with gpx file. '
                               'Please delete and re-import the gpx file.'
                }
                code = 500
                return jsonify(response_object), code

            activity = edit_activity_wo_gpx(activity, activity_data)
            db.session.commit()
            response_object = {
                'status': 'success',
                'data': {
                    'activities': [activity.serialize()]
                }
            }
            code = 200
        else:
            response_object = {
                'status': 'not found',
                'data': {
                    'activities': []
                }
            }
            code = 404
    except (exc.IntegrityError, exc.OperationalError, ValueError) as e:
        db.session.rollback()
        appLog.error(e)
        response_object = {
            'status': 'error',
            'message': 'Error. Please try again or contact the administrator.'
        }
        code = 500
    return jsonify(response_object), code


@activities_blueprint.route(
    '/activities/<int:activity_id>', methods=['DELETE']
)
@authenticate
def delete_activity(auth_user_id, activity_id):
    """Delete an activity"""
    try:
        activity = Activity.query.filter_by(id=activity_id).first()
        if activity:
            gpx_filepath = activity.gpx
            db.session.delete(activity)
            db.session.commit()

            if gpx_filepath:
                os.remove(gpx_filepath)

            response_object = {
                'status': 'no content'
            }
            code = 204
        else:
            response_object = {
                'status': 'not found',
                'data': {
                    'activities': []
                }
            }
            code = 404
    except (exc.IntegrityError, exc.OperationalError, ValueError, OSError) \
            as e:
        db.session.rollback()
        appLog.error(e)
        response_object = {
            'status': 'error',
            'message': 'Error. Please try again or contact the administrator.'
        }
        code = 500
    return jsonify(response_object), code
