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
        weather_info = self.provider.get_info()

        # items in weather info exist
        for item in weather_info:
            self.assertIsNotNone(item)

        # items are in proper type
        self.assertTrue(type(weather_info['Temperature']) is int)
        self.assertTrue(type(weather_info['RealFeel']) is int)
        self.assertTrue(type(weather_info['Condition']) is str)


    def test_get_hourly(self):
        """ get_hourly test """

        URL = self.provider.URL_hourly
        self.provider.raw_page = self.provider.get_raw_page(URL, True)
        weather_info = self.provider.get_hourly()

        # items in weather info exist
        for item in weather_info:
            self.assertIsNotNone(item)

        # items are in proper type
        self.assertTrue(type(weather_info['Max']) is int)
        self.assertTrue(type(weather_info['Min']) is int)
        self.assertTrue(type(weather_info['Av']) is float)
        self.assertTrue(type(weather_info['Num']) is int)

        # max greater than min, av is between max and min
        self.assertGreaterEqual(weather_info['Max'], weather_info['Min'])
        self.assertLessEqual(weather_info['Av'], weather_info['Max'])
        self.assertLessEqual(weather_info['Min'], weather_info['Av'])


    def test_get_next_day(self):
        """ get_next_day test """

        URL = self.provider.URL_next_day
        self.provider.raw_page = self.provider.get_raw_page(URL, True)
        weather_info = self.provider.get_next_day()

        # items in weather info exist
        for item in weather_info:
            self.assertIsNotNone(item)

        # items are in proper type
        self.assertTrue(type(weather_info['Next_day_temp']) is int)
        self.assertTrue(type(weather_info['Next_day_RF']) is int)
        self.assertTrue(type(weather_info['Next_day_condition']) is str)
        self.assertTrue(type(weather_info['Next_night_temp']) is int)
        self.assertTrue(type(weather_info['Next_night_RF']) is int)
        self.assertTrue(type(weather_info['Next_night_condition']) is str)


    def test_get_current_location(self):
        """ get_current_location test """

        URL = self.provider.URL
        self.provider.raw_page = self.provider.get_raw_page(URL, True)
        location = self.provider.get_current_location()

        # check if list returned
        self.assertTrue(type(location) is list)
        # check item type of location
        for item in location:
            self.assertTrue(type(item) is str)


if __name__ == "__main__":
    unittest.main()
