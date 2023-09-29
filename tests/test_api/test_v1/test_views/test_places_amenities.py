#!/usr/bin/python3
"""
Contains the TestPlaces_AmenitiesDocs classes
"""

from api.v1.app import app
from api.v1.views import places_amenities
from datetime import datetime
import inspect
from models import storage
from models.place import Place
import pep8
import unittest


class TestPlaces_AmenitiesDocs(unittest.TestCase):
    """Tests to check the documentation and style of places_amenities"""
    @classmethod
    def setUpClass(cls):
        """Set up for the doc tests"""
        cls.state_f = inspect.getmembers(places_amenities, inspect.isfunction)

    def test_pep8_conformance_places_amenities(self):
        """Test that api/v1/views/places_amenities.py conforms to PEP8."""
        pep8s = pep8.StyleGuide(quiet=True)
        result = pep8s.check_files(['api/v1/views/places_amenities.py'])
        self.assertEqual(result.total_errors, 0,
                         "Found code style errors (and warnings).")

    def test_pep8_conformance_test_places_amenities(self):
        """Test that tests/test_api/test_v1/test_views/test_places_amenities.py
        conforms to PEP8."""
        pep8s = pep8.StyleGuide(quiet=True)
        result = pep8s.check_files(
                ['tests/test_api/test_v1/test_views/test_places_amenities.py'])
        self.assertEqual(result.total_errors, 0,
                         "Found code style errors (and warnings).")

    def test_places_amenities_module_docstring(self):
        """Test for the places_amenities.py module docstring"""
        self.assertIsNot(places_amenities.__doc__, None,
                         "places_amenities.py needs a docstring")
        self.assertTrue(len(places_amenities.__doc__) >= 1,
                        "places_amenities.py needs a docstring")

    def test_state_func_docstrings(self):
        """Test for the presence of docstrings in Places_Amenities methods"""
        for func in self.state_f:
            self.assertIsNot(func[1].__doc__, None,
                             "{:s} method needs a docstring".format(func[0]))
            self.assertTrue(len(func[1].__doc__) >= 1,
                            "{:s} method needs a docstring".format(func[0]))


class TestPlaces_AmenitiesRoutes(unittest.TestCase):
    """Test the places_amenities api routes"""
    @classmethod
    def setUpClass(cls):
        """Set up for the route tests"""
        cls.app = app.test_client()
        cls.api = "/api/v1/places/"
        app.config['TESTING'] = True

    def setUp(self) -> None:
        """Prepopulate places and amenities, link some"""
        self.amenities = [self.app.post("/api/v1/amenities",
                                        json={"name": f"Amenity {i}"}).json
                          for i in range(0, 5)]
        self.state = self.app.post("/api/v1/states",
                                   json={"name": "Test State"}).json
        self.user = self.app.post("/api/v1/users",
                                  json={"email": "Test User",
                                        "password": "Test password"}).json
        self.city = self.app.post("/api/v1/states/{}/cities"
                                  .format(self.state['id']),
                                  json={"name": "Test City"}).json
        self.places = [self.app.post("/api/v1/cities/{}/places"
                                     .format(self.city['id']),
                                     json={"name": f"Place {i}",
                                           "user_id": self.user['id']}).json
                       for i in range(0, 3)]
        # link first 2 places to some amenities
        for i in range(0, 2):
            for j in range(0, i+3):
                x = self.app.post("/api/v1/places/{}/amenities/{}"
                                  .format(self.places[i]['id'],
                                          self.amenities[j]['id']))

    @classmethod
    def tearDownClass(cls):
        """tearDownClass"""
        storage.close()

    def test_places_amenities_route(self):
        """Test /places/<place_id>/amenities GET"""
        places_amenities = self.app.get("{}{}/amenities"
                                        .format(self.api,
                                                self.places[0]['id']))
        self.assertEqual(places_amenities.status_code, 200)
        # Ensure list is returned
        self.assertIsInstance(places_amenities.json, list)

    def test_fail_places_amenities_route(self):
        """Test /places/<place_id>/amenities GET failure"""
        places_amenities = self.app.get("{}{}/amenities"
                                        .format(self.api,
                                                "nop"))
        self.assertEqual(places_amenities.status_code, 404)

    def test_link_places_amenities_route(self):
        """Test /places/<place_id>/amenities/<amenity_id> POST"""
        prev_pa = self.app.get("{}{}/amenities"
                               .format(self.api,
                                       self.places[0]['id']))
        # New amenity
        new_amenity = self.app.post("{}{}/amenities/{}"
                                    .format(self.api,
                                            self.places[0]['id'],
                                            self.amenities[-1]['id']))
        self.assertEqual(new_amenity.status_code, 201)
        new_pa = self.app.get("{}{}/amenities"
                              .format(self.api,
                                      self.places[0]['id']))
        self.assertEqual(len(prev_pa.json) + 1, len(new_pa.json))
        # Repeat anemity should not insert
        repeat_amenity = self.app.post("{}{}/amenities/{}"
                                       .format(self.api,
                                               self.places[0]['id'],
                                               self.amenities[-1]['id']))
        self.assertEqual(repeat_amenity.status_code, 200)
        repeat_pa = self.app.get("{}{}/amenities"
                                 .format(self.api,
                                         self.places[0]['id']))
        self.assertEqual(len(repeat_pa.json), len(new_pa.json))

    def test_fail_link_places_amenities_route(self):
        """Test /places/<place_id>/amenities/<amenity_id> POST failure"""
        amenity = self.app.post("{}{}/amenities/{}"
                                .format(self.api,
                                        "nop",
                                        self.amenities[-1]['id']))
        self.assertEqual(amenity.status_code, 404)
        amenity = self.app.post("{}{}/amenities/{}"
                                .format(self.api,
                                        self.places[0]['id'],
                                        "nop"))
        self.assertEqual(amenity.status_code, 404)

    def test_delete_places_amenities_by_id_route(self):
        """Test /places/<place_id>/amenities/<amenity_id> DELETE"""
        prev_pa = self.app.get("{}{}/amenities"
                               .format(self.api,
                                       self.places[0]['id']))
        delete_amenity = self.app.delete("{}{}/amenities/{}"
                                         .format(self.api,
                                                 self.places[0]['id'],
                                                 self.amenities[0]['id']))
        self.assertEqual(delete_amenity.status_code, 200)
        new_pa = self.app.get("{}{}/amenities"
                              .format(self.api,
                                      self.places[0]['id']))
        self.assertEqual(len(new_pa.json) + 1, len(prev_pa.json))

    def test_fail_delete_places_amenities_by_id_route(self):
        """Test /places/<place_id>/amenities/<amenity_id> DELETE failure"""
        delete_amenity = self.app.delete("{}{}/amenities/{}"
                                         .format(self.api,
                                                 "nop",
                                                 self.amenities[0]['id']))
        self.assertEqual(delete_amenity.status_code, 404)
        delete_amenity = self.app.delete("{}{}/amenities/{}"
                                         .format(self.api,
                                                 self.places[0]['id'],
                                                 "nop"))
        self.assertEqual(delete_amenity.status_code, 404)
