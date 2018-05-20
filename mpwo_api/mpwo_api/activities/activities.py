import json
import os

from flask import Blueprint, jsonify, request
from mpwo_api import appLog, db
from sqlalchemy import exc

from ..users.utils import authenticate, verify_extension
from .models import Activity, Sport
from .utils import (
    create_activity, create_segment, edit_activity, get_file_path,
    get_gpx_info, get_new_file_path
)

activities_blueprint = Blueprint('activities', __name__)


@activities_blueprint.route('/activities', methods=['GET'])
@authenticate
def get_activities(auth_user_id):
    """Get all activities for authenticated user"""
    try:
        params = request.args.copy()
        page = 1 if len(params) == 0 else int(params.pop('page'))
        activities = Activity.query.filter_by(user_id=auth_user_id)\
            .order_by(Activity.activity_date.desc()).paginate(
            page, 5, False).items
        response_object = {
            'status': 'success',
            'data': {
                'activities': [activity.serialize() for activity in activities]
            }
        }
        code = 200
    except Exception as e:
        appLog.error(e)
        response_object = {
            'status': 'error',
            'message': 'Error. Please try again or contact the administrator.'
        }
        code = 500
    return jsonify(response_object), code


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
    """Post an activity (with gpx file)"""
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

        if gpx_data is None:
            response_object = {
                'status': 'error',
                'message': 'Error during gpx file parsing.'
            }
            return jsonify(response_object), 500

        sport = Sport.query.filter_by(id=activity_data.get('sport_id')).first()
        new_filepath = get_new_file_path(
            auth_user_id=auth_user_id,
            activity_date=gpx_data['start'],
            activity_file=activity_file,
            sport=sport.label
        )
        os.rename(file_path, new_filepath)
        gpx_data['filename'] = new_filepath
    except Exception as e:
        appLog.error(e)
        response_object = {
            'status': 'error',
            'message': 'Error during activity file save.'
        }
        return jsonify(response_object), 500

    try:
        new_activity = create_activity(
            auth_user_id, activity_data, gpx_data)
        db.session.add(new_activity)
        db.session.flush()

        for segment_data in gpx_data['segments']:
            new_segment = create_segment(new_activity.id, segment_data)
            db.session.add(new_segment)
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
    if not activity_data:
        response_object = {
            'status': 'error',
            'message': 'Invalid payload.'
        }
        return jsonify(response_object), 400

    try:
        activity = Activity.query.filter_by(id=activity_id).first()
        if activity:
            activity = edit_activity(activity, activity_data)
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
