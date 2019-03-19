import sys
sys.path.insert(0, '..')

import unittest

from abstract.providers import AccuProvider
from app import App

class TestAccuProvider(unittest.TestCase):
    """ Test case for AccuProvider """

    def setUp(self):
        self.app = App()
        self.provider = AccuProvider(self.app)

    def test_get_info(self):
        """ get_info test """

        # Let download a page from Accu web site
        URL = self.provider.URL
        self.provider.raw_page = self.provider.get_raw_page(URL, True)
        # Test
        weather_info = self.provider.get_info()
        for item in weather_info:
            self.assertTrue(item)
        self.assertTrue(type(weather_info['Temperature']) is int)
        self.assertTrue(type(weather_info['RealFeel']) is int)
        self.assertTrue(type(weather_info['Condition']) is str)

if __name__ == "__main__":
    unittest.main()
