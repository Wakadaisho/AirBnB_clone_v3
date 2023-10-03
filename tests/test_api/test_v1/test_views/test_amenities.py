#!/usr/bin/python3
"""
Contains the TestAmenityDocs classes
"""

from api.v1.app import app
from api.v1.views import amenities
from datetime import datetime
import inspect
from models import storage
import pep8
import unittest


class TestAmenitysDocs(unittest.TestCase):
    """Tests to check the documentation and style of amenities"""
    @classmethod
    def setUpClass(cls):
        """Set up for the doc tests"""
        cls.amenity_f = inspect.getmembers(amenities, inspect.isfunction)

    def test_pep8_conformance_amenities(self):
        """Test that api/v1/views/amenities.py conforms to PEP8."""
        pep8s = pep8.StyleGuide(quiet=True)
        result = pep8s.check_files(['api/v1/views/amenities.py'])
        self.assertEqual(result.total_errors, 0,
                         "Found code style errors (and warnings).")

    def test_pep8_conformance_test_amenities(self):
        """Test that tests/test_api/test_v1/test_views/test_amenities.py
        conforms to PEP8."""
        pep8s = pep8.StyleGuide(quiet=True)
        result = pep8s.check_files(
                ['tests/test_api/test_v1/test_views/test_amenities.py'])
        self.assertEqual(result.total_errors, 0,
                         "Found code style errors (and warnings).")

    def test_amenities_module_docstring(self):
        """Test for the amenities.py module docstring"""
        self.assertIsNot(amenities.__doc__, None,
                         "amenities.py needs a docstring")
        self.assertTrue(len(amenities.__doc__) >= 1,
                        "amenities.py needs a docstring")

    def test_amenity_func_docstrings(self):
        """Test for the presence of docstrings in Amenity methods"""
        for func in self.amenity_f:
            self.assertIsNot(func[1].__doc__, None,
                             "{:s} method needs a docstring".format(func[0]))
            self.assertTrue(len(func[1].__doc__) >= 1,
                            "{:s} method needs a docstring".format(func[0]))


class TestAmenityRoutes(unittest.TestCase):
    """Test the amenities api routes"""
    @classmethod
    def setUpClass(cls):
        """Set up for the route tests"""
        cls.app = app.test_client()
        cls.api = "/api/v1/amenities/"
        app.config['TESTING'] = True

    @classmethod
    def tearDownClass(cls):
        """tearDownClass"""
        storage.close()

    def setUp(self):
        """Prepopulate some amenities"""
        self.amenities = [self.app.post(self.api,
                                        json={"name": "Amenity {}"
                                              .format(i)}).json
                          for i in range(0, 5)]

    def test_amenities_route(self):
        """Test /amenities GET"""
        amenities = self.app.get(self.api)
        self.assertEqual(amenities.status_code, 200)
        self.assertIsInstance(amenities.json, list)

    def test_amenity_route(self):
        """Test /amenities/<amenity_id> GET"""
        amenity = self.app.get(self.api + self.amenities[0]['id'])
        self.assertEqual(amenity.status_code, 200)
        self.assertIsInstance(amenity.json, dict)
        self.assertEqual(amenity.json['id'], self.amenities[0]['id'])

    def test_fail_amenity_route(self):
        """Test /amenities/<amenity_id> GET failure"""
        amenity = self.app.get(self.api + "nop")
        self.assertEqual(amenity.status_code, 404)

    def test_post_amenities_route(self):
        """Test /amenities/<state_id> POST"""
        post_amenity = self.app.post(self.api,
                                     json={"name": "Amenity 5"})
        self.assertEqual(post_amenity.status_code, 201)
        amenity = self.app.get(self.api + post_amenity.json['id'])
        self.assertEqual(amenity.status_code, 200)

    def test_fail_post_amenities_route(self):
        """Test /amenities POST failure"""
        amenity = self.app.post(self.api, json="")
        self.assertEqual(amenity.status_code, 400)
        self.assertEqual(amenity.json['error'], "Not a JSON")
        amenity = self.app.post(self.api, json={"names": "Amenity 5"})
        self.assertEqual(amenity.status_code, 400)
        self.assertEqual(amenity.json['error'], "Missing name")

    def test_put_amenities_by_id_route(self):
        """Test /amenities/<amenity_id> PUT"""
        amenity = self.app.put(self.api + self.amenities[0]['id'],
                               json={"name": "Amenity 99"})
        self.assertEqual(amenity.status_code, 200)
        self.assertEqual(amenity.json['id'], self.amenities[0]['id'])
        self.assertEqual(amenity.json['name'], "Amenity 99")

    def test_fail_put_amenities_by_id_route(self):
        """Test /amenities/<amenity_id> PUT failure"""
        amenity = self.app.put(self.api + "nop",
                               json={"name": "Amenity 99"})
        self.assertEqual(amenity.status_code, 404)

        amenity = self.app.put(self.api + self.amenities[0]['id'],
                               json="")
        self.assertEqual(amenity.status_code, 400)
        self.assertEqual(amenity.json['error'], "Not a JSON")

    def test_delete_amenities_by_id_route(self):
        """Test /amenities/<amenity_id> DELETE"""
        delete_amenity = self.app.delete(self.api + self.amenities[0]['id'])
        self.assertEqual(delete_amenity.status_code, 200)
        self.assertIsInstance(delete_amenity.json, dict)
        amenity = self.app.get(self.api + self.amenities[0]['id'])
        self.assertEqual(amenity.status_code, 404)
        self.assertEqual(amenity.json['error'], "Not found")

    def test_fail_delete_amenities_by_id_route(self):
        """Test /amenities/<amenity_id> DELETE failure"""
        amenity = self.app.delete(self.api + "nop")
        self.assertEqual(amenity.status_code, 404)
        self.assertEqual(amenity.json['error'], "Not found")
