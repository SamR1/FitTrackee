from flask import Blueprint, jsonify

from ..users.utils import authenticate
from .models import Record

records_blueprint = Blueprint('records', __name__)


@records_blueprint.route('/records', methods=['GET'])
@authenticate
def get_records(auth_user_id):
    """Get all records for authenticated user"""
    records = Record.query.filter_by(user_id=auth_user_id)\
        .order_by(
        Record.sport_id.asc(),
        Record.record_type.asc(),
        ).all()
    response_object = {
        'status': 'success',
        'data': {
            'records': [record.serialize() for record in records]
        }
    }
    return jsonify(response_object), 200
