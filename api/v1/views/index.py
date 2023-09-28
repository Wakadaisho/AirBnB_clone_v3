#!/usr/bin/python3
"""
Define routes for the v1 API
"""

from api.v1.views import app_views
from flask import jsonify


@app_views.route("/status", strict_slashes=False)
def status():
    """Return the operational status of the api endpoint"""
    return jsonify({"status": "OK"}), 200
