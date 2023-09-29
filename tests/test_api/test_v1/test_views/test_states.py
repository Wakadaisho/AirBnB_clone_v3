#!/usr/bin/python3
"""
Contains the TestStateDocs classes
"""

from api.v1.app import app
from api.v1.views import states
from datetime import datetime
import inspect
from models import storage
import pep8
import unittest


class TestStatesDocs(unittest.TestCase):
    """Tests to check the documentation and style of states"""
    @classmethod
    def setUpClass(cls):
        """Set up for the doc tests"""
        cls.state_f = inspect.getmembers(states, inspect.isfunction)

    def test_pep8_conformance_states(self):
        """Test that api/v1/views/states.py conforms to PEP8."""
        pep8s = pep8.StyleGuide(quiet=True)
        result = pep8s.check_files(['api/v1/views/states.py'])
        self.assertEqual(result.total_errors, 0,
                         "Found code style errors (and warnings).")

    def test_pep8_conformance_test_states(self):
        """Test that tests/test_api/test_v1/test_views/test_states.py
        conforms to PEP8."""
        pep8s = pep8.StyleGuide(quiet=True)
        result = pep8s.check_files(
                ['tests/test_api/test_v1/test_views/test_states.py'])
        self.assertEqual(result.total_errors, 0,
                         "Found code style errors (and warnings).")

    def test_states_module_docstring(self):
        """Test for the states.py module docstring"""
        self.assertIsNot(states.__doc__, None,
                         "states.py needs a docstring")
        self.assertTrue(len(states.__doc__) >= 1,
                        "states.py needs a docstring")

    def test_state_func_docstrings(self):
        """Test for the presence of docstrings in State methods"""
        for func in self.state_f:
            self.assertIsNot(func[1].__doc__, None,
                             "{:s} method needs a docstring".format(func[0]))
            self.assertTrue(len(func[1].__doc__) >= 1,
                            "{:s} method needs a docstring".format(func[0]))


class TestStateRoutes(unittest.TestCase):
    """Test the states api routes"""
    @classmethod
    def setUpClass(cls):
        """Set up for the route tests"""
        cls.app = app.test_client()
        cls.api = "/api/v1/states/"
        app.config['TESTING'] = True

    @classmethod
    def tearDownClass(cls):
        """tearDownClass"""
        storage.close()

    def test_states_route(self):
        """Test /states GET"""
        default_states = self.app.get(self.api)
        self.assertEqual(default_states.status_code, 200)
        # Ensure list is returned
        self.assertIsInstance(default_states.json, list)

    def test_post_states_route(self):
        """Test /states POST"""
        default_states = self.app.get(self.api)
        self.assertEqual(default_states.status_code, 200)
        post_state = self.app.post(self.api,
                                   json={"name": "Test"})
        self.assertEqual(post_state.status_code, 201)
        new_states = self.app.get(self.api)
        self.assertEqual(new_states.status_code, 200)
        # Ensure count stat of state increased by one
        self.assertEqual(len(default_states.json) + 1,
                         len(new_states.json))

    def test_fail_post_states_route(self):
        """Test /states POST failure"""
        default_states = self.app.get(self.api)
        self.assertEqual(default_states.status_code, 200)
        state = self.app.post(self.api, json="")
        self.assertEqual(state.status_code, 400)
        self.assertEqual(state.json['error'], "Not a JSON")
        state = self.app.post(self.api, json={"names": "Test"})
        self.assertEqual(state.status_code, 400)
        self.assertEqual(state.json['error'], "Missing name")
        new_states = self.app.get(self.api)

    def test_states_by_id_route(self):
        """Test /states/<state_id> GET"""
        post_state = self.app.post(self.api,
                                   json={"name": "Test"})
        self.assertEqual(post_state.status_code, 201)
        new_state = self.app.get(self.api + post_state.json['id'])
        self.assertEqual(new_state.status_code, 200)
        self.assertEqual(new_state.json['id'], post_state.json['id'])
        self.assertEqual(new_state.json['name'], "Test")

    def test_fail_state_id_route(self):
        """Test /states/<state_id> GET failure"""
        state = self.app.get(self.api + "nop")
        self.assertEqual(state.status_code, 404)

    def test_put_states_by_id_route(self):
        """Test /states/<state_id> PUT"""
        post_state = self.app.post(self.api,
                                   json={"name": "Test"})
        self.assertEqual(post_state.status_code, 201)
        new_state = self.app.get(self.api + post_state.json['id'])
        self.assertEqual(new_state.status_code, 200)
        self.assertIsInstance(new_state.json, dict)
        self.assertEqual(new_state.json['id'], post_state.json['id'])
        self.assertEqual(new_state.json['name'], "Test")
        put_state = self.app.put(self.api + post_state.json['id'],
                                 json={"name": "Test edited"})
        self.assertEqual(put_state.status_code, 200)
        self.assertEqual(put_state.json['id'], post_state.json['id'])
        self.assertEqual(put_state.json['name'], "Test edited")

    def test_fail_put_states_by_id_route(self):
        """Test /states/<state_id> PUT failure"""
        post_state = self.app.post(self.api,
                                   json={"name": "Test"})
        self.assertEqual(post_state.status_code, 201)
        # Test non-existent id
        put_state = self.app.put(self.api + "nop",
                                 json="")
        self.assertEqual(put_state.status_code, 404)
        put_state = self.app.put(self.api + post_state.json['id'],
                                 json="")
        self.assertEqual(put_state.status_code, 400)
        self.assertEqual(put_state.json['error'], "Not a JSON")

    def test_delete_states_by_id_route(self):
        """Test /states/<state_id> DELETE"""
        post_state = self.app.post(self.api,
                                   json={"name": "Test"})
        self.assertEqual(post_state.status_code, 201)
        delete_state = self.app.delete(self.api + post_state.json['id'])
        self.assertEqual(delete_state.status_code, 200)
        self.assertIsInstance(delete_state.json, dict)
        state = self.app.get(self.api + post_state.json['id'])
        self.assertEqual(state.status_code, 404)

    def test_fail_delete_states_by_id_route(self):
        """Test /states/<state_id> DELETE failure"""
        state = self.app.delete(self.api + "nop")
        self.assertEqual(state.status_code, 404)
