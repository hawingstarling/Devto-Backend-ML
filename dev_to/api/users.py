from http import HTTPStatus
from flask import Blueprint, Response, jsonify, make_response
from matplotlib.font_manager import json_dump, json_load
from bson import json_util

from . import delete_user
from . import db, get_user, get_users, update_user, delete_user

users_api_v1 = Blueprint('user_api_v1', __name__)


@users_api_v1.route('/')
def index():
    return '/api/v1 routes user'


@users_api_v1.route('/user/<id>', methods=['GET'])
def get_user_by_id(id):
    user = get_user(id)
    if user is None:
        return jsonify({
            'error': 'Not found'
        }), 400
    elif user == {}:
        return jsonify({
            'error': 'Uncaught general exception'
        }), 400
    else: 
        return make_response(json_util.dumps({
            'user': user
        }), HTTPStatus.OK)

def obj_dict(obj):
    return obj.__dict__

@users_api_v1.route('/users', methods=['GET'])
def get_all_users():

    return make_response(json_util.dumps({
        'users': get_users()
    }, default=obj_dict), HTTPStatus.OK)

    # --> Alternative
    # response = json_util.dumps(get_users())
    # return Response(
    #     response,
    #     mimetype='application/json'
    # )

