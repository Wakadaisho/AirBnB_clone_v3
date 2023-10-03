#!/usr/bin/python3
"""
Contains the TestUserDocs classes
"""

from api.v1.app import app
from api.v1.views import places
from datetime import datetime
import inspect
from models import storage, storage_t
from models.amenity import Amenity
from models.city import City
from models.state import State
from models.place import Place
from models.user import User
from random import randrange
import pep8
import unittest


class TestUsersDocs(unittest.TestCase):
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
        """Test for the presence of docstrings in User methods"""
        for func in self.place_f:
            self.assertIsNot(func[1].__doc__, None,
                             "{:s} method needs a docstring".format(func[0]))
            self.assertTrue(len(func[1].__doc__) >= 1,
                            "{:s} method needs a docstring".format(func[0]))


class TestUserRoutes(unittest.TestCase):
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
        state = State(name="Test State")
        state.save()
        city = City(name="Test City", state_id=state.id)
        city.save()
        data = {"name": "New Place"}
        user = User(email="Test User", password="password")
        user.save()
        response = self.app.post(f"/api/v1/cities/{city.id}/places", json=data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['error'], "Missing user_id")
        data = {"user_id": user.id}
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

    def test_places_search(self):
        """Test /places_search"""
        results = self.app.post("/api/v1/places_search",
                                json="")
        self.assertEqual(results.status_code, 400)
        self.assertEqual(results.json['error'], "Not a JSON")

        results = self.app.post("/api/v1/places_search",
                                json={})
        self.assertEqual(results.status_code, 200)
        self.assertIsInstance(results.json, list)

        states = []
        for i in range(2):
            state = State(name=f"State {i}")
            state.save()
            states.append(state.id)

        cities = []
        for i in range(5):
            j = 1 if i >= 2 else 0
            city = City(name=f"City {i}", state_id=states[j])
            city.save()
            cities.append(city.id)

        user = User(email="email", password="password")
        user.save()

        amenities = []
        for i in range(50):
            amenity = Amenity(name=f"Amenity {i}")
            amenity.save()
            amenities.append(amenity)

        places = []
        for i, city in enumerate(cities):
            for j in range(0, i+1):
                place = Place(name=f"Place {i}{j}",
                              user_id=user.id,
                              city_id=city)
                for k in range(5):
                    if storage_t == 'db':
                        place.amenities.append(amenities[i * j + k])
                    else:
                        place.amenities = amenities[i * j + k]
                place.save()
                places.append(place.id)

        results = self.app.post("/api/v1/places_search",
                                json={"states": [states[0]],
                                      "cities": [cities[3]]})

        self.assertEqual(results.status_code, 200)
        self.assertEqual(len(results.json), 7)
        filter_amenities = [amenities[randrange(5)].id
                            for _ in range(5)]
        results = self.app.post("/api/v1/places_search",
                                json={"states": [states[0]],
                                      "cities": [cities[3]],
                                      "amenities": filter_amenities
                                      })
        self.assertEqual(results.status_code, 200)
        places = [storage.get(Place, place['id']) for place in results.json]
        for place in places:
            for am in filter_amenities:
                if storage_t == 'db':
                    self.assertTrue(
                            am in [a.to_dict()['id'] for a in place.amenities])
                else:
                    self.assertTrue(am in place.amenities)

        results = self.app.post("/api/v1/places_search",
                                json={"amenities": filter_amenities[0:1]})
        self.assertEqual(results.status_code, 200)
        places = [storage.get(Place, place['id']) for place in results.json]

        for place in places:
            for am in filter_amenities[0:1]:
                if storage_t == 'db':
                    self.assertTrue(
                            am in [a.to_dict()['id'] for a in place.amenities])
                else:
                    self.assertTrue(am in place.amenities)
