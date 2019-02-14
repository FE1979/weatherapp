import unittest

from abstract.abstract import WeatherProvider, Formatter
from app import App

class TestProvider(WeatherProvider):
    """ Test provider """

    title = "Accuweather"
    Location = "Test Location"
    args = ""

    def get_info(self):
        """ described abstract function
        """
        return {"Info": "Parsed"}

    def get_hourly(self):
        """ described abstract function
        """
        return {"Info": "Parsed hourly"}

    def get_next_day(self):
        """ described abstract function
        """
        return {"Info": "Parsed next day"}

    def browse_location(self, level = 0, URL_location = None):
        """ described abstract function
        """
        pass

    def set_location(self, location_set):
        """ described abstract function """
        pass


class ABC_Formatter(Formatter):
    """ Fake Formatter class to test """

    def print_out(self):
        return self.headers_dict


class TestWeatherProvider(unittest.TestCase):
    """ WeatherProvider abstract class unit test """

    def setUp(self):
        self.app = App()
        self.test_provider = TestProvider(self.app)

    def test_get_raw_page(self):
        """ Test loading page """

        for title in ['Accuweather', 'RP5', 'Sinoptik']:
            TestProvider.title = title
            self.test_provider = TestProvider(self.app)
            page = self.test_provider.get_raw_page(self.test_provider.URL)
            self.assertNotEqual(page, "")

    def test_run(self):
        """ Testing run of WeatherProvider abstract class """

        weather_info = {}
        self.test_provider = TestProvider(self.app)
        title = self.test_provider.title
        city = self.test_provider.Location

        cli_args = ['-next', '-f'] # set cli args for test provider

        for cli_arg in cli_args: # run each command to test
            self.test_provider.app.remaining_args.append(cli_arg)
            self.test_provider.get_cli_args()
            refresh = self.test_provider.args.refresh

            if self.test_provider.args.next:
                self.raw_page = self.test_provider.get_raw_page(
                                        self.test_provider.URL_next_day, refresh)
                info_next_day = self.test_provider.get_next_day()
                weather_info.update(info_next_day)
                title = title + ", прогноз на завтра, " + city

            if not self.test_provider.args.next:
                self.raw_page = self.test_provider.get_raw_page(
                                        self.test_provider.URL, refresh)
                weather_info.update(self.test_provider.get_info())
                title = title + ", поточна погода, " + city
                if self.test_provider.args.forec:
                    self.raw_page = self.test_provider.get_raw_page(
                                        self.test_provider.URL_hourly, refresh)
                    weather_info.update(self.test_provider.get_hourly())

            if self.test_provider.app.remaining_args.pop() == '-next':
                self.assertEqual(weather_info, {"Info": "Parsed next day"})
            else:
                self.assertEqual(weather_info, {"Info": "Parsed hourly"})


class TestFormatter(unittest.TestCase):
    """ Test Formatter """

    def setUp(self):
        self.formatter = ABC_Formatter()

    def test_print_out(self):
        self.assertEqual(self.formatter.headers_dict, self.formatter.print_out())


if __name__ == "__main__":
    unittest.main()
