#!/usr/bin/python3
"""
Contains the TestStateDocs classes
"""

from api.v1.app import app
from api.v1.views import index
from datetime import datetime
import inspect
import pep8
import unittest

from models import storage


class TestIndexDocs(unittest.TestCase):
    """Tests to check the documentation and style of index"""
    @classmethod
    def setUpClass(cls):
        """Set up for the doc tests"""
        cls.index_f = inspect.getmembers(index, inspect.isfunction)

    def test_pep8_conformance_index(self):
        """Test that api/v1/views/index.py conforms to PEP8."""
        pep8s = pep8.StyleGuide(quiet=True)
        result = pep8s.check_files(['api/v1/views/index.py'])
        self.assertEqual(result.total_errors, 0,
                         "Found code style errors (and warnings).")

    def test_pep8_conformance_test_index(self):
        """Test that tests/test_api/test_v1/test_views/test_index.py
        conforms to PEP8."""
        pep8s = pep8.StyleGuide(quiet=True)
        result = pep8s.check_files(
                ['tests/test_api/test_v1/test_views/test_index.py'])
        self.assertEqual(result.total_errors, 0,
                         "Found code style errors (and warnings).")

    def test_index_module_docstring(self):
        """Test for the index.py module docstring"""
        self.assertIsNot(index.__doc__, None,
                         "index.py needs a docstring")
        self.assertTrue(len(index.__doc__) >= 1,
                        "index.py needs a docstring")

    def test_index_func_docstrings(self):
        """Test for the presence of docstrings in index routes"""
        for func in self.index_f:
            self.assertIsNot(func[1].__doc__, None,
                             "{:s} method needs a docstring".format(func[0]))
            self.assertTrue(len(func[1].__doc__) >= 1,
                            "{:s} method needs a docstring".format(func[0]))


class TestIndex(unittest.TestCase):
    """Test the index api routes"""
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

    def test_status_route(self):
        """Test /status GET"""
        endpoint = self.api + "/status"
        status = self.app.get(endpoint)
        self.assertEqual(status.status_code, 200)

    def test_stats_route(self):
        """Test /stats GET"""
        endpoint = self.api + "/stats"
        default_stats = self.app.get(endpoint)
        self.assertEqual(default_stats.status_code, 200)
        post_state = self.app.post(self.api + "/states",
                                   json={"name": "Ohio"})
        self.assertEqual(post_state.status_code, 201)
        new_stats = self.app.get(endpoint)
        self.assertEqual(new_stats.status_code, 200)
        # Ensure count stat of state increased by one
        self.assertEqual(default_stats.json['states'] + 1,
                         new_stats.json['states'])
