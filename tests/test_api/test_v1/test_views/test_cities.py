#!/usr/bin/python3
"""
Contains the TestCityDocs classes
"""

from api.v1.app import app
from api.v1.views import cities
from datetime import datetime
import inspect
from models import storage
import pep8
import unittest


class TestCitysDocs(unittest.TestCase):
    """Tests to check the documentation and style of cities"""
    @classmethod
    def setUpClass(cls):
        """Set up for the doc tests"""
        cls.city_f = inspect.getmembers(cities, inspect.isfunction)

    def test_pep8_conformance_cities(self):
        """Test that api/v1/views/cities.py conforms to PEP8."""
        pep8s = pep8.StyleGuide(quiet=True)
        result = pep8s.check_files(['api/v1/views/cities.py'])
        self.assertEqual(result.total_errors, 0,
                         "Found code style errors (and warnings).")

    def test_pep8_conformance_test_cities(self):
        """Test that tests/test_api/test_v1/test_views/test_cities.py
        conforms to PEP8."""
        pep8s = pep8.StyleGuide(quiet=True)
        result = pep8s.check_files(
                ['tests/test_api/test_v1/test_views/test_cities.py'])
        self.assertEqual(result.total_errors, 0,
                         "Found code style errors (and warnings).")

    def test_cities_module_docstring(self):
        """Test for the cities.py module docstring"""
        self.assertIsNot(cities.__doc__, None,
                         "cities.py needs a docstring")
        self.assertTrue(len(cities.__doc__) >= 1,
                        "cities.py needs a docstring")

    def test_city_func_docstrings(self):
        """Test for the presence of docstrings in City methods"""
        for func in self.city_f:
            self.assertIsNot(func[1].__doc__, None,
                             "{:s} method needs a docstring".format(func[0]))
            self.assertTrue(len(func[1].__doc__) >= 1,
                            "{:s} method needs a docstring".format(func[0]))


class TestCityRoutes(unittest.TestCase):
    """Test the cities api routes"""
    @classmethod
    def setUpClass(cls):
        """Set up for the route tests"""
        cls.app = app.test_client()
        cls.api = "/api/v1"
        app.config['TESTING'] = True

    @classmethod
    def tearDownClass(cls):
        """tearDownClass"""
        storage.close()

    def setUp(self):
        """Create some states for cities and prepopulate"""
        self.state_1 = self.app.post(self.api + "/states",
                                     json={"name": "Test State 1"})
        self.state_2 = self.app.post(self.api + "/states",
                                     json={"name": "Test State 2"})
        # Make 3 cities for state 1
        for i in range(0, 3):
            self.app.post(self.api + "/states/{}/cities"
                          .format(self.state_1.json['id']),
                          json={"name": f"This city {i}"})
        # Make 3 cities for state 2
        for i in range(0, 5):
            self.app.post(self.api + "/states/{}/cities"
                          .format(self.state_2.json['id']),
                          json={"name": f"That city {i}"})

    def test_cities_route(self):
        """Test /states/<state_id>/cities GET"""
        state_1_cities = self.app.get(self.api + "/states/{}/cities"
                                      .format(self.state_1.json['id']))
        self.assertEqual(state_1_cities.status_code, 200)
        self.assertIsInstance(state_1_cities.json, list)
        state_2_cities = self.app.get(self.api + "/states/{}/cities"
                                      .format(self.state_2.json['id']))
        self.assertEqual(state_2_cities.status_code, 200)
        self.assertIsInstance(state_2_cities.json, list)

    def test_fail_cities_route(self):
        """Test /states/<state_id>/cities GET failure"""
        nop_cities = self.app.get(self.api + "/states/{}/cities"
                                  .format("nop"))
        self.assertEqual(nop_cities.status_code, 404)
        self.assertEqual(nop_cities.json['error'], "Not found")

    def test_city_route(self):
        """Test /cities/<city_id> GET"""
        state_1_cities = self.app.get(self.api + "/states/{}/cities"
                                      .format(self.state_1.json['id']))
        first_city = state_1_cities.json[0]
        city = self.app.get(self.api + "/cities/{}"
                            .format(first_city['id']))
        self.assertEqual(city.status_code, 200)
        self.assertIsInstance(city.json, dict)
        self.assertEqual(city.json['id'], first_city['id'])

    def test_fail_city_route(self):
        """Test /cities/<city_id> GET failure"""
        city = self.app.get(self.api + "/cities/{}"
                            .format("nop"))
        self.assertEqual(city.status_code, 404)

    def test_post_cities_route(self):
        """Test /states/<state_id>/cities POST"""
        post_city = self.app.post(self.api + "/states/{}/cities"
                                  .format(self.state_1.json['id']),
                                  json={"name": "This city 4"})
        self.assertEqual(post_city.status_code, 201)
        city = self.app.get(self.api + "/cities/{}"
                            .format(post_city.json['id']))
        self.assertEqual(city.status_code, 200)
        self.assertEqual(city.json['state_id'], self.state_1.json['id'])

    def test_fail_post_cities_route(self):
        """Test /states/<state_id>/cities POST failure"""
        city = self.app.post(self.api + "/states/{}/cities"
                             .format("nop"),
                             json={"name": "This city 4"})
        self.assertEqual(city.status_code, 404)
        city = self.app.post(self.api + "/states/{}/cities"
                             .format(self.state_1.json['id']),
                             json="")
        self.assertEqual(city.status_code, 400)
        self.assertEqual(city.json['error'], "Not a JSON")
        city = self.app.post(self.api + "/states/{}/cities"
                             .format(self.state_1.json['id']),
                             json={"names": "This city 4"})
        self.assertEqual(city.status_code, 400)
        self.assertEqual(city.json['error'], "Missing name")

    def test_put_cities_by_id_route(self):
        """Test /cities/<city_id> PUT"""
        state_1_cities = self.app.get(self.api + "/states/{}/cities"
                                      .format(self.state_1.json['id']))
        first_city = state_1_cities.json[0]
        city = self.app.put(self.api + "/cities/{}"
                            .format(first_city['id']),
                            json={"name": "Oh, This city 1"})
        self.assertEqual(city.status_code, 200)
        self.assertEqual(city.json['id'], first_city['id'])
        self.assertEqual(city.json['name'], "Oh, This city 1")

    def test_fail_put_cities_by_id_route(self):
        """Test /cities/<city_id> PUT failure"""
        state_1_cities = self.app.get(self.api + "/states/{}/cities"
                                      .format(self.state_1.json['id']))
        first_city = state_1_cities.json[0]
        city = self.app.put(self.api + "/cities/{}"
                            .format("nop"),
                            json={"name": "Oh, This city 1"})
        self.assertEqual(city.status_code, 404)

        city = self.app.put(self.api + "/cities/{}"
                            .format(first_city['id']),
                            json="")
        self.assertEqual(city.status_code, 400)
        self.assertEqual(city.json['error'], "Not a JSON")

    def test_delete_cities_by_id_route(self):
        """Test /cities/<city_id> DELETE"""
        state_1_cities = self.app.get(self.api + "/states/{}/cities"
                                      .format(self.state_1.json['id']))
        first_city = state_1_cities.json[0]
        delete_city = self.app.delete(self.api + "/cities/{}"
                                      .format(first_city['id']))
        self.assertEqual(delete_city.status_code, 200)
        self.assertIsInstance(delete_city.json, dict)
        city = self.app.get(self.api + first_city['id'])
        self.assertEqual(city.status_code, 404)
        self.assertEqual(city.json['error'], "Not found")

    def test_fail_delete_cities_by_id_route(self):
        """Test /cities/<city_id> DELETE failure"""
        city = self.app.get(self.api + "/cities/nop")
        self.assertEqual(city.status_code, 404)
        self.assertEqual(city.json['error'], "Not found")
