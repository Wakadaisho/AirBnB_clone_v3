#!/usr/bin/python3
"""
Reviews module
"""

from api.v1.views import app_views
from flask import jsonify, abort, request, make_response
from models import storage
from models.user import User
from models.review import Review
from models.place import Place


@app_views.route('/places/<place_id>/reviews')
def get_reviews_by_place(place_id):
    """ Retrives list of reviews of a place """
    place = storage.get(Place, place_id)
    if place is None:
        abort(404)
    reviews = [obj.to_dict() for obj in place.reviews]
    return jsonify(reviews)


@app_views.route('/reviews/<review_id>', methods=['GET'])
def get_review_by_id(review_id):
    """ Retrieve a review by id """
    review = storage.get(Review, review_id)
    if review is None:
        abort(404)
    return jsonify(review.to_dict())


@app_views.route('/reviews/<review_id>', methods=['DELETE'])
def delete_review_by_id(review_id):
    """ Deletes review by id """
    review = storage.get(Review, review_id)
    if review is None:
        abort(404)
    review.delete()
    storage.save()
    return jsonify({}), 200


@app_views.route('/places/<place_id>/reviews', methods=['POST'])
def create_review(place_id):
    """ creates a new review for a place """
    place = storage.get(Place, place_id)
    if place is None:
        abort(404)
    data = request.get_json()
    if not data:
        return make_response(jsonify({"error": "Not a JSON"}), 400)
    if 'user_id' not in data:
        return make_response(jsonify({"error": "Missing user_id"}), 400)
    user = storage.get(User, data['user_id'])
    if user is None:
        abort(404)
    if 'text' not in data:
        return make_response(jsonify({"error": "Missing text"}), 400)
    data['place_id'] = place_id
    new_review = Review(**data)
    new_review.save()
    return (jsonify(new_review.to_dict()), 201)


@app_views.route('/reviews/<review_id>', methods=['PUT'])
def update_review_by_id(review_id):
    """ Updates a review obj by its ID """
    if not request.get_json():
        return make_response(jsonify({"error": "Not a JSON"}), 400)
    review = storage.get(Review, review_id)
    if review is None:
        abort(404)
    for key, value in request.get_json().items():
        if key not in ['id', 'user_id', 'city_id', 'created_at', 'updated']:
            setattr(review, key, value)
    storage.save()
    return jsonify(review.to_dict()), 200
