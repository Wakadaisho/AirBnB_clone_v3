#!/usr/bin/python3
"""
Contains the TestStateDocs classes
"""

from api.v1.app import app
from api.v1.views import places
from datetime import datetime
import inspect
from models import storage
from models.city import City
from models.place import Place
from models.user import User
import pep8
import unittest


class TestStatesDocs(unittest.TestCase):
    """Tests to check the documentation and style of places"""
    @classmethod
    def setUpClass(cls):
        """Set up for the doc tests"""
        cls.place_f = inspect.getmembers(places, inspect.isfunction)

    def test_pep8_conformance_places(self):
        """Test that api/v1/views/places.py conforms to PEP8."""
        pep8s = pep8.StyleGuide(quiet=True)
        result = pep8s.check_files(['api/v1/views/places.py'])
        self.assertEqual(result.total_errors, 0,
                         "Found code style errors (and warnings).")

    def test_pep8_conformance_test_places(self):
        """Test that tests/test_api/test_v1/test_views/test_places.py
        conforms to PEP8."""
        pep8s = pep8.StyleGuide(quiet=True)
        result = pep8s.check_files(
                ['tests/test_api/test_v1/test_views/test_places.py'])
        self.assertEqual(result.total_errors, 0,
                         "Found code style errors (and warnings).")

    def test_places_module_docstring(self):
        """Test for the places.py module docstring"""
        self.assertIsNot(places.__doc__, None,
                         "places.py needs a docstring")
        self.assertTrue(len(places.__doc__) >= 1,
                        "places.py needs a docstring")

    def test_place_func_docstrings(self):
        """Test for the presence of docstrings in State methods"""
        for func in self.place_f:
            self.assertIsNot(func[1].__doc__, None,
                             "{:s} method needs a docstring".format(func[0]))
            self.assertTrue(len(func[1].__doc__) >= 1,
                            "{:s} method needs a docstring".format(func[0]))


class TestStateRoutes(unittest.TestCase):
    """Test the places api routes"""
    @classmethod
    def setUpClass(cls):
        """Set up for the route tests"""
        cls.app = app.test_client()
        cls.api = "/api/v1/places/"
        app.config['TESTING'] = True

    @classmethod
    def tearDownClass(cls):
        """tearDownClass"""
        storage.close()

    def test_create_place_missing_fields(self):
        """Test /cities/<city_id>/places POST missing fields"""
        city = City(name="Test City")
        city.save()
        data = {"name": "New Place"}
        response = self.app.post(f"/api/v1/cities/{city.id}/places", json=data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['error'], "Missing user_id")
        data = {"user_id": 1}
        response = self.app.post(f"/api/v1/cities/{city.id}/places", json=data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['error'], "Missing name")

    def test_fail_place_id_route(self):
        """Test /places/<place_id> GET failure"""
        place = self.app.get(self.api + "nop")
        self.assertEqual(place.status_code, 404)

    def test_fail_delete_places_by_id_route(self):
        """Test /places/<place_id> DELETE failure"""
        place = self.app.delete(self.api + "nop")
        self.assertEqual(place.status_code, 404)
