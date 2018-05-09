import json
import os
from datetime import datetime, timedelta

from flask import Blueprint, current_app, jsonify, request
from mpwo_api import appLog, db
from sqlalchemy import exc
from werkzeug.utils import secure_filename

from ..users.utils import authenticate, verify_extension
from .models import Activity
from .utils import get_gpx_info

activities_blueprint = Blueprint('activities', __name__)


def create_activity_with_gpx(auth_user_id, gpx_data, file_path, sport_id):
    new_activity = Activity(
        user_id=auth_user_id,
        sport_id=sport_id,
        activity_date=gpx_data['start'],
        duration=timedelta(seconds=gpx_data['duration'])
    )
    new_activity.gpx = file_path
    new_activity.pauses = timedelta(seconds=gpx_data['stop_time'])
    new_activity.moving = timedelta(seconds=gpx_data['moving_time'])
    new_activity.distance = gpx_data['distance']
    new_activity.min_alt = gpx_data['elevation_min']
    new_activity.max_alt = gpx_data['elevation_max']
    new_activity.descent = gpx_data['downhill']
    new_activity.ascent = gpx_data['uphill']
    new_activity.max_speed = gpx_data['max_speed']
    new_activity.ave_speed = gpx_data['average_speed']
    return new_activity


def create_activity_wo_gpx(auth_user_id, activity_data):
    new_activity = Activity(
        user_id=auth_user_id,
        sport_id=activity_data.get('sport_id'),
        activity_date=datetime.strptime(
            activity_data.get('activity_date'), '%Y-%m-%d %H:%M'),
        duration=timedelta(seconds=activity_data.get('duration'))
    )
    new_activity.moving = new_activity.duration
    new_activity.distance = activity_data.get('distance')
    new_activity.ave_speed = new_activity.distance / (
        new_activity.duration.seconds / 3600)
    new_activity.max_speed = new_activity.ave_speed
    return new_activity


def get_file_path(auth_user_id, activity_file):
    filename = secure_filename(activity_file.filename)
    dir_path = os.path.join(
        current_app.config['UPLOAD_FOLDER'], 'activities', str(auth_user_id))
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    file_path = os.path.join(dir_path, filename)
    return file_path


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
    '/activities/<int:activity_id>/gpx',
    methods=['GET']
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
        new_activity = create_activity_with_gpx(
            auth_user_id, gpx_data, file_path, activity_data.get('sport_id'))
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
        new_activity = create_activity_wo_gpx(auth_user_id, activity_data)
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
