#!/usr/bin/python3
"""
Define routes for the v1 API
"""

from api.v1.views import app_views
from flask import jsonify
from models import storage
from models.amenity import Amenity
from models.city import City
from models.place import Place
from models.review import Review
from models.state import State
from models.user import User


@app_views.route("/status")
def status():
    """Return the operational status of the api endpoint"""
    return jsonify({"status": "OK"}), 200


@app_views.route("/stats")
def stats():
    """Return the operational status of the api endpoint"""
    classes = {"amenities": Amenity, "cities": City,
               "places": Place, "reviews": Review,
               "states": State, "users": User}
    return jsonify({k: storage.count(v) for k, v in classes.items()}), 200
