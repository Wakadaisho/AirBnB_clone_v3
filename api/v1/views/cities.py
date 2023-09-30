#!/usr/bin/python3
"""
Define routes for the City object
"""

from api.v1.views import app_views
from flask import abort, request, jsonify
from models import storage
from models.city import City
from models.state import State


@app_views.route("/states/<state_id>/cities")
def select_city_by_state(state_id):
    """Return cities in a state if exists"""
    state = storage.get(State, state_id)
    if not state:
        abort(404)
    return jsonify([city.to_dict() for city in state.cities])


@app_views.route("/cities/<city_id>")
def select_city(city_id):
    """Return a city object of id city_id if exists"""
    city = storage.get(City, city_id)
    if not city:
        abort(404)
    return jsonify(city.to_dict())


@app_views.route("/cities/<city_id>", methods=["DELETE"])
def drop_city(city_id):
    """Delete a City object"""
    city = storage.get(City, city_id)
    if not city:
        abort(404)
    city.delete()
    storage.save()
    return jsonify({}), 200


@app_views.route("/states/<state_id>/cities", methods=["POST"])
def insert_city(state_id):
    """Create a City object"""
    state = storage.get(State, state_id)
    if not state:
        abort(404)
    obj = request.get_json()
    if not obj:
        return jsonify({"error": "Not a JSON"}), 400
    if "name" not in obj:
        return jsonify({"error": "Missing name"}), 400
    city = City(**obj)
    city.state_id = state_id
    city.save()
    return jsonify(city.to_dict()), 201


@app_views.route("/cities/<city_id>", methods=["PUT"])
def update_city(city_id):
    """Update a City object"""
    attrs = ['name']
    obj = request.get_json()
    if not obj:
        return jsonify({"error": "Not a JSON"}), 400
    city = storage.get(City, city_id)
    ignore = ["id", "created_at", "state_id", "updated_at"]
    if city is None:
        abort(404)
    for attr in attrs:
        if (attr in obj and attr not in ignore):
            setattr(city, attr, obj[attr])
    city.save()
    return jsonify(city.to_dict()), 200
