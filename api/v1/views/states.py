#!/usr/bin/python3
"""
Define routes for the State object
"""

from api.v1.views import app_views
from flask import abort, request
from models import storage
from models.state import State


@app_views.route("/states")
def states():
    """Return all the state objects"""
    return [state.to_dict() for state in storage.all(State).values()]


@app_views.route("/states/<state_id>")
def select_state(state_id):
    """Return a state object of id state_id if exists"""
    state = storage.get(State, state_id)
    if not state:
        abort(404)
    return state.to_dict()


@app_views.route("/states/<state_id>", methods=["DELETE"])
def drop_state(state_id):
    """Delete a State object"""
    state = storage.get(State, state_id)
    if not state:
        abort(404)
    storage.delete(state)
    storage.save()
    return {}, 200


@app_views.route("/states", methods=["POST"])
def insert_state():
    """Create a State object"""
    obj = request.get_json()
    if not obj:
        return {"error": "Not a JSON"}, 400
    if "name" not in obj:
        return {"error": "Missing name"}, 400
    state = State(**obj)
    state.save()
    return state.to_dict(), 201


@app_views.route("/states/<state_id>", methods=["PUT"])
def update_state(state_id):
    """Update a State object"""
    attrs = ['name']
    obj = request.get_json()
    if not obj:
        return {"error": "Not a JSON"}, 400
    state = storage.get(State, state_id)
    if state is None:
        abort(404)
    for attr in attrs:
        if attr in obj:
            setattr(state, attr, obj[attr])
    state.save()
    return state.to_dict(), 200
