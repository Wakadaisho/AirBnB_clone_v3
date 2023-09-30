#!/usr/bin/python3
"""
Define routes for the Amenity object
"""

from api.v1.views import app_views
from flask import abort, request, jsonify
from models import storage
from models.amenity import Amenity


@app_views.route("/amenities")
def get_all_amenities():
    """Return all the amenity objects"""
    return jsonify([amenity.to_dict()
                    for amenity in storage.all(Amenity).values()]), 200


@app_views.route("/amenities/<amenity_id>")
def select_amenity(amenity_id):
    """Return a amenity object of id amenity_id if exists"""
    amenity = storage.get(Amenity, amenity_id)
    if not amenity:
        abort(404)
    return jsonify(amenity.to_dict()), 200


@app_views.route("/amenities/<amenity_id>", methods=["DELETE"])
def drop_amenity(amenity_id):
    """Delete a Amenity object"""
    amenity = storage.get(Amenity, amenity_id)
    if not amenity:
        abort(404)
    amenity.delete()
    storage.save()
    return jsonify({}), 200


@app_views.route("/amenities", methods=["POST"])
def insert_amenity():
    """Create a Amenity object"""
    obj = request.get_json()
    if not obj:
        return jsonify({"error": "Not a JSON"}), 400
    if "name" not in obj:
        return jsonify({"error": "Missing name"}), 400
    amenity = Amenity(**obj)
    amenity.save()
    return jsonify(amenity.to_dict()), 201


@app_views.route("/amenities/<amenity_id>", methods=["PUT"])
def update_amenity(amenity_id):
    """Update a Amenity object"""
    attrs = ['name']
    obj = request.get_json()
    if not obj:
        return jsonify({"error": "Not a JSON"}), 400
    amenity = storage.get(Amenity, amenity_id)
    if amenity is None:
        abort(404)
    for attr in attrs:
        if attr in obj and attr not in ["id", "created_at", "updated_at"]:
            setattr(amenity, attr, obj[attr])
    amenity.save()
    return jsonify(amenity.to_dict()), 200
