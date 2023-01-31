import unittest
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


