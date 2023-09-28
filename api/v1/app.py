#!/usr/bin/python3
"""
Module for APIs
"""

from api.v1.views import app_views
from flask import Flask, make_response, jsonify
from models import storage
from os import getenv

app = Flask(__name__)
app.register_blueprint(app_views)


@app.teardown_appcontext
def teardown_appcontext(excpetion):
    """Teardown instance"""
    storage.close()

@app.errorhandler(404)
def not_found(error):
    """ Error handler route"""
    return make_response(jsonify({'error': 'Not found'}), 404)


if __name__ == "__main__":
    app.run(host=getenv("HBNB_API_HOST", "0.0.0.0"),
            port=getenv("HBNB_API_PORT", 5000),
            threaded=True)
