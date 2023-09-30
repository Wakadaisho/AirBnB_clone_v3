#!/usr/bin/python3
"""
Define routes for the places_amenities routes
"""

from api.v1.views import app_views
from flask import abort, jsonify
from models import storage, storage_t
from models.amenity import Amenity
from models.place import Place


@app_views.route("/places/<place_id>/amenities")
def get_all_place_amenities(place_id):
    """Return all the amenity in a place"""
    place = storage.get(Place, place_id)
    if not place:
        abort(404)
    data = []
    if storage_t == 'db':
        data = [amenity.to_dict() for amenity in place.amenities]
    else:
        data = [storage.get(Amenity, id).to_dict() for id in place.amenities]
    return jsonify(data)


@app_views.route("/places/<place_id>/amenities/<amenity_id>",
                 methods=['POST'])
def post_place(place_id, amenity_id):
    """Associate a place with an amenity"""
    place = storage.get(Place, place_id)
    amenity = storage.get(Amenity, amenity_id)
    if not (amenity and place):
        abort(404)

    for a in place.amenities:
        if storage_t == 'db' and a.id == amenity_id:
            return jsonify(a.to_dict())
        elif a == amenity_id:
            return jsonify(storage.get(Amenity, a).to_dict())

    if storage_t == 'db':
        place.amenities.append(amenity)
    else:
        place.amenities = amenity

    storage.save()
    return jsonify(amenity.to_dict()), 201


@app_views.route("/places/<place_id>/amenities/<amenity_id>",
                 methods=["DELETE"])
def drop_place_amenity(place_id, amenity_id):
    """Delete a Place Amenity association"""
    place = storage.get(Place, place_id)
    amenity = storage.get(Amenity, amenity_id)
    if not (amenity and place):
        abort(404)

    for a in place.amenities:
        if storage_t == 'db' and a.id == amenity_id:
            place.amenities.remove(a)
            storage.save()
            return jsonify({}), 200
        elif a == amenity_id:
            amenities = place.amenities.copy()
            amenities.remove(a)
            place.amenities = amenities
            storage.save()
            return jsonify({}), 200

    abort(404)
