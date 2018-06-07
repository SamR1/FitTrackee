import json
import os
import shutil
from datetime import datetime, timedelta

from fittrackee_api import appLog, db
from flask import Blueprint, current_app, jsonify, request, send_file
from sqlalchemy import exc

from ..users.utils import authenticate, verify_extension
from .models import Activity
from .utils import (
    ActivityException, create_activity, edit_activity, get_chart_data,
    process_files
)
from .utils_format import convert_in_duration

activities_blueprint = Blueprint('activities', __name__)


@activities_blueprint.route('/activities', methods=['GET'])
@authenticate
def get_activities(auth_user_id):
    """Get all activities for authenticated user"""
    try:
        params = request.args.copy()
        page = 1 if 'page' not in params.keys() else int(params.get('page'))
        date_from = params.get('from')
        date_to = params.get('to')
        distance_from = params.get('distance_from')
        distance_to = params.get('distance_to')
        duration_from = params.get('duration_from')
        duration_to = params.get('duration_to')
        ave_speed_from = params.get('ave_speed_from')
        ave_speed_to = params.get('ave_speed_to')
        order = params.get('order')
        sport_id = params.get('sport_id')
        per_page = int(params.get('per_page')) if params.get('per_page') else 5
        activities = Activity.query.filter(
            Activity.user_id == auth_user_id,
            Activity.sport_id == sport_id if sport_id else True,
            Activity.activity_date >= datetime.strptime(date_from, '%Y-%m-%d')
            if date_from else True,
            Activity.activity_date < (
                datetime.strptime(date_to, '%Y-%m-%d') + timedelta(days=1)
            ) if date_to else True,
            Activity.distance >= int(distance_from) if distance_from else True,
            Activity.distance <= int(distance_to) if distance_to else True,
            Activity.duration >= convert_in_duration(duration_from)
            if duration_from else True,
            Activity.duration <= convert_in_duration(duration_to)
            if duration_to else True,
            Activity.ave_speed >= float(ave_speed_from)
            if ave_speed_from else True,
            Activity.ave_speed <= float(ave_speed_to)
            if ave_speed_to else True,
        ).order_by(
            Activity.activity_date.asc()
            if order == 'asc'
            else Activity.activity_date.desc()
        ).paginate(
            page, per_page, False
        ).items
        response_object = {
            'status': 'success',
            'data': {
                'activities': [activity.serialize(params)
                               for activity in activities]
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


def get_activity_data(auth_user_id, activity_id, data_type):
    """Get chart data from an activity gpx file"""
    activity = Activity.query.filter_by(id=activity_id).first()
    content = ''
    if activity:
        if not activity.gpx or activity.gpx == '':
            response_object = {
                'status': 'fail',
                'message': f'No gpx file for this activity (id: {activity_id})'
            }
            return jsonify(response_object), 400

        try:
            if data_type == 'chart':
                content = get_chart_data(activity.gpx)
            else:  # data_type == 'gpx'
                with open(activity.gpx, encoding='utf-8') as f:
                    content = f.read()
        except Exception as e:
            appLog.error(e)
            response_object = {'status': 'error',
                               'message': 'internal error',
                               'data': ({'chart_data': content}
                                        if data_type == 'chart'
                                        else {'gpx': content})}
            return jsonify(response_object), 500

        status = 'success'
        message = ''
        code = 200
    else:
        status = 'not found'
        message = f'Activity not found (id: {activity_id})'
        code = 404

    response_object = {'status': status,
                       'message': message,
                       'data': ({'chart_data': content}
                                if data_type == 'chart'
                                else {'gpx': content})}
    return jsonify(response_object), code


@activities_blueprint.route(
    '/activities/<int:activity_id>/gpx', methods=['GET']
)
@authenticate
def get_activity_gpx(auth_user_id, activity_id):
    """Get gpx file for an activity"""
    return get_activity_data(auth_user_id, activity_id, 'gpx')


@activities_blueprint.route(
    '/activities/<int:activity_id>/chart_data', methods=['GET']
)
@authenticate
def get_activity_chart_data(auth_user_id, activity_id):
    """Get chart data from an activity gpx file"""
    return get_activity_data(auth_user_id, activity_id, 'chart')


@activities_blueprint.route('/activities/map/<map_id>', methods=['GET'])
def get_map(map_id):
    try:
        activity = Activity.query.filter_by(map_id=map_id).first()
        if not activity:
            response_object = {
                'status': 'fail',
                'message': 'Map does not exist'
            }
            return jsonify(response_object), 404
        else:
            return send_file(activity.map)
    except Exception as e:
        appLog.error(e)
        response_object = {
            'status': 'error',
            'message': 'internal error.'
        }
        return jsonify(response_object), 500


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
    upload_dir = os.path.join(
        current_app.config['UPLOAD_FOLDER'],
        'activities',
        str(auth_user_id))
    folders = {
        'extract_dir': os.path.join(upload_dir, 'extract'),
        'tmp_dir': os.path.join(upload_dir, 'tmp'),
    }

    try:
        new_activities = process_files(
            auth_user_id, activity_data, activity_file, folders
        )
        if len(new_activities) > 0:
            response_object = {
                'status': 'created',
                'data': {
                    'activities': [new_activity.serialize()
                                   for new_activity in new_activities]
                }
            }
            code = 201
        else:
            response_object = {
                'status': 'fail',
                'data': {
                    'activities': []
                }
            }
            code = 400
    except ActivityException as e:
        db.session.rollback()
        if e.e:
            appLog.error(e.e)
        response_object = {
            'status': e.status,
            'message': e.message,
        }
        code = 500 if e.status == 'error' else 400

    shutil.rmtree(folders['extract_dir'], ignore_errors=True)
    shutil.rmtree(folders['tmp_dir'], ignore_errors=True)
    return jsonify(response_object), code


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
            db.session.delete(activity)
            db.session.commit()
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
