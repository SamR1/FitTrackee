import json
import os
from datetime import timedelta

from flask import Blueprint, current_app, jsonify, request
from mpwo_api import appLog, db
from sqlalchemy import exc
from werkzeug.utils import secure_filename

from ..users.utils import authenticate, verify_extension
from .models import Activity
from .utils import get_gpx_info

activities_blueprint = Blueprint('activities', __name__)


@activities_blueprint.route('/activities', methods=['GET'])
@authenticate
def get_activities(auth_user_id):
    """Get all activities"""
    activities = Activity.query.all()
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
        response_object = {
            'status': 'success',
            'data': {
                'activities': activities_list
            }
        }
        code = 200
    else:
        response_object = {
            'status': 'not found',
            'data': {
                'activities': activities_list
            }
        }
        code = 404
    return jsonify(response_object), code


@activities_blueprint.route('/activities', methods=['POST'])
@authenticate
def post_activity(auth_user_id):
    """Post an activity"""
    code = 400
    response_object = verify_extension('activity', request)
    if response_object['status'] != 'success':
        return jsonify(response_object), code

    activity_data = json.loads(request.form["data"])
    if not activity_data or activity_data.get('sport_id') is None:
        response_object = {
            'status': 'error',
            'message': 'Invalid payload.'
        }
        return jsonify(response_object), 400

    activity_file = request.files['file']
    filename = secure_filename(activity_file.filename)
    dirpath = os.path.join(
        current_app.config['UPLOAD_FOLDER'],
        'activities',
        str(auth_user_id)
    )
    if not os.path.exists(dirpath):
        os.makedirs(dirpath)
    filepath = os.path.join(dirpath, filename)

    try:
        activity_file.save(filepath)
        gpx_data = get_gpx_info(filepath)
    except Exception as e:
        appLog.error(e)
        response_object = {
            'status': 'error',
            'message': 'Error during activity file save.'
        }
        return jsonify(response_object), 500

    try:
        new_activity = Activity(
            user_id=auth_user_id,
            sport_id=activity_data.get('sport_id'),
            activity_date=gpx_data['start'],
            duration=timedelta(seconds=gpx_data['duration'])
        )
        new_activity.gpx = filepath
        new_activity.pauses = timedelta(seconds=gpx_data['stop_time'])
        new_activity.moving = timedelta(seconds=gpx_data['moving_time'])
        new_activity.distance = gpx_data['distance']
        new_activity.min_alt = gpx_data['elevation_min']
        new_activity.max_alt = gpx_data['elevation_max']
        new_activity.descent = gpx_data['downhill']
        new_activity.ascent = gpx_data['uphill']
        new_activity.max_speed = gpx_data['max_speed']
        new_activity.ave_speed = gpx_data['average_speed']
        db.session.add(new_activity)
        db.session.commit()

        response_object = {
            'status': 'created',
            'message': 'Activity added.'
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
