import unittest
# import mock
from unittest import mock
import sys
from promua_fetcher.order_fetcher import init_parameters
from promua_fetcher.order_fetcher import MySQLClient
from promua_fetcher.order_fetcher import PromuaAPIClient


class TestArgParser(unittest.TestCase):
    """Suite for testing command line arguments parser"""

    def test_Version(self):
        """Checking '--version' argument"""
        sys.argv[1:] = ['--version']
        with self.assertRaises(SystemExit, msg="'--version' parameter parsed in wrong way"):
            init_parameters()

    def test_Mode(self):
        """Checking parsing URL parameter"""
        sys.argv[1:] = ['fetch']
        options = init_parameters()
        self.assertEqual(options.mode, 'fetch', "Failure to pass mode from command line")


class TestMySQLClient(unittest.TestCase):

    @mock.patch('mysql.connector.connect')
    def test_connect_db(self, mockconnect):
        client = MySQLClient("TEST_DB_HOST", "TEST_DB_PORT", "TEST_DB_NAME", "TEST_DB_USER", "TEST_DB_PASS")
        connection = client.connect_db()
        self.assertIsNotNone(connection)
        mockconnect.assert_called()


