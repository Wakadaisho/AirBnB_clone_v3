#!/usr/bin/python3
"""
Contains the TestStateDocs classes
"""

from api.v1.app import app
from api.v1.views import users
from datetime import datetime
import inspect
from models import storage
import pep8
import unittest


class TestStatesDocs(unittest.TestCase):
    """Tests to check the documentation and style of users"""
    @classmethod
    def setUpClass(cls):
        """Set up for the doc tests"""
        cls.user_f = inspect.getmembers(users, inspect.isfunction)

    def test_pep8_conformance_users(self):
        """Test that api/v1/views/users.py conforms to PEP8."""
        pep8s = pep8.StyleGuide(quiet=True)
        result = pep8s.check_files(['api/v1/views/users.py'])
        self.assertEqual(result.total_errors, 0,
                         "Found code style errors (and warnings).")


    def test_users_module_docstring(self):
        """Test for the users.py module docstring"""
        self.assertIsNot(users.__doc__, None,
                         "users.py needs a docstring")
        self.assertTrue(len(users.__doc__) >= 1,
                        "users.py needs a docstring")

    def test_user_func_docstrings(self):
        """Test for the presence of docstrings in State methods"""
        for func in self.user_f:
            self.assertIsNot(func[1].__doc__, None,
                             "{:s} method needs a docstring".format(func[0]))
            self.assertTrue(len(func[1].__doc__) >= 1,
                            "{:s} method needs a docstring".format(func[0]))


class TestStateRoutes(unittest.TestCase):
    """Test the users api routes"""
    @classmethod
    def setUpClass(cls):
        """Set up for the route tests"""
        cls.app = app.test_client()
        cls.api = "/api/v1/users/"
        app.config['TESTING'] = True

    @classmethod
    def tearDownClass(cls):
        """tearDownClass"""
        storage.close()

    def test_users_route(self):
        """Test /users GET"""
        default_users = self.app.get(self.api)
        self.assertEqual(default_users.status_code, 200)
        # Ensure list is returned
        self.assertIsInstance(default_users.json, list)


    def test_fail_user_id_route(self):
        """Test /users/<user_id> GET failure"""
        user = self.app.get(self.api + "nop")
        self.assertEqual(user.status_code, 404)

    def test_fail_delete_users_by_id_route(self):
        """Test /users/<user_id> DELETE failure"""
        user = self.app.delete(self.api + "nop")
        self.assertEqual(user.status_code, 404)
