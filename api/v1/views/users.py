#!/usr/bin/python3
"""
User module
"""

from api.v1.views import app_views
from flask import jsonify, abort, request, make_response
from models import storage
from models.user import User


@app_views.route('/users', methods=['GET'])
def get_users():
    """Gets list of all user objs"""
    users = storage.all(User)
    user_lst = [user.to_dict() for user in users.values()]
    return jsonify(user_lst)


@app_views.route('/users/<user_id>', methods=['GET'])
def get_user_by_id(user_id):
    """ Retrieves a user by ID """
    user = storage.get(User, user_id)
    if user:
        return jsonify(user.to_dict())
    else:
        abort(404)


@app_views.route('/users/<user_id>', methods=['DELETE'])
def delete_user_by_id(user_id):
    """Deletes a User object by ID """
    user = storage.get(User, user_id)
    if user:
        user.delete()
        storage.save()
        return jsonify({}), 200
    else:
        abort(404)


@app_views.route('/users', methods=['POST'])
def create_user():
    """Create a new user."""
    if not request.get_json():
        return make_response(jsonify({"error": "Not a JSON"}), 400)
    if 'email' not in request.get_json():
        return make_response(jsonify({"error": "Missing email"}), 400)
    if 'password'not in request.get_json():
        return make_response(jsonify({"error": "Missing password"}), 400)
    data = request.get_json()
    new_user = User(**data)
    new_user.save()
    return jsonify(new_user.to_dict()), 201


@app_views.route('/users/<user_id>', methods=['PUT'])
def update_user_by_id(user_id):
    """ Updates a User object by ID """
    user = storage.get(User, user_id)
    if user:
        data = request.get_json()
        if not data:
            return make_response(jsonify({"error": "Not a JSON"}), 400)
        ignore_keys = ['id', 'email', 'created_at', 'updated_at']
        for key, value in data.items():
            if key not in ignore_keys:
                setattr(user, key, value)
        storage.save()
        return jsonify(user.to_dict()), 200
    else:
        abort(404)
