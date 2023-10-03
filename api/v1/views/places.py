#!/usr/bin/python3
"""
Place module
"""

from api.v1.views import app_views
from flask import jsonify, abort, request, make_response
from models import storage, storage_t
from models.user import User
from models.city import City
from models.place import Place
from models.state import State


@app_views.route('/cities/<city_id>/places', methods=['GET'])
def get_places_by_city(city_id):
    """ Retrives list of cities by id """
    city = storage.get(City, city_id)
    if city is None:
        abort(404)
    places = [place.to_dict() for place in city.places]
    return jsonify(places)


@app_views.route('/places/<place_id>', methods=['GET'])
def get_place_by_id(place_id):
    """ Retrieve a place by id """
    place = storage.get(Place, place_id)
    if place is None:
        abort(404)
    return jsonify(place.to_dict())


@app_views.route('/places/<place_id>', methods=['DELETE'])
def delete_place_by_id(place_id):
    """ Deletes place by id """
    place = storage.get(Place, place_id)
    if place is None:
        abort(404)
    place.delete()
    storage.save()
    return jsonify({}), 200


@app_views.route('/cities/<city_id>/places', methods=['POST'])
def create_place(city_id):
    """ creates a new place """
    city = storage.get(City, city_id)
    if city is None:
        abort(404)
    data = request.get_json()
    if not data:
        return make_response(jsonify({"error": "Not a JSON"}), 400)
    if 'user_id' not in data:
        return make_response(jsonify({"error": "Missing user_id"}), 400)
    user = storage.get(User, data['user_id'])
    if user is None:
        abort(404)
    if 'name' not in data:
        return make_response(jsonify({"error": "Missing name"}), 400)
    data['city_id'] = city_id
    new_place = Place(**data)
    new_place.save()
    return (jsonify(new_place.to_dict()), 201)


@app_views.route('/places/<place_id>', methods=['PUT'])
def update_place_by_id(place_id):
    """ Updates place obj by its ID """
    place = storage.get(Place, place_id)
    if place is None:
        abort(404)
    if not request.get_json():
        return make_response(jsonify({"error": "Not a JSON"}), 400)
    for key, value in request.get_json().items():
        if key not in ['id', 'user_id', 'city_id', 'created_at', 'updated_at']:
            setattr(place, key, value)
    storage.save()
    return jsonify(place.to_dict()), 200


@app_views.route('/places_search', methods=['POST'])
def search_places_by_id():
    """ search places by id """
    data = request.get_json()

    if not data and type(data) is not dict:
        return make_response(jsonify({"error": "Not a JSON"}), 400)

    states = data.get('states', [])
    cities = data.get('cities', [])
    amenities = data.get('amenities', [])
    places = []

    if (len(states) + len(cities)) == 0:
        places = [place for place in storage.all(Place).values()]
    else:
        cities = {storage.get(City, i) for i in cities if storage.get(City, i)}
        cities = cities.union({city
                               for s in [storage.get(State, i)
                                         for i in states
                                         if storage.get(State, i)]
                               for city in s.cities})
        places = [place
                  for city in cities
                  for place in city.places]

    if storage_t == 'db':
        places = [place.to_dict() for place in places
                  if all([amenity in [am.to_dict()['id']
                                      for am in place.amenities]
                          for amenity in amenities])]
    else:
        places = [place.to_dict() for place in places
                  if all([amenity in [am for am in place.amenities]
                          for amenity in amenities])]

    for place in places:
        place.pop("amenities", None)
    places = [] if not places else places
    return jsonify(places)
