from flask import Blueprint, jsonify

from ..users.utils import authenticate
from .models import Record

records_blueprint = Blueprint('records', __name__)


@records_blueprint.route('/records', methods=['GET'])
@authenticate
def get_sports(auth_user_id):
    """Get all records for authenticated user"""
    records = Record.query.filter_by(user_id=auth_user_id)\
        .order_by(Record.record_type).all()
    records_list = []
    for record in records:
        records_list.append(record.serialize())
    response_object = {
        'status': 'success',
        'data': {
            'records': records_list
        }
    }
    return jsonify(response_object), 200
