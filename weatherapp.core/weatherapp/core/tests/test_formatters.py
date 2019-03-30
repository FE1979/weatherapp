import sys
sys.path.insert(0, '..')

import unittest

from managers.formatters import TableFormatter, PlainText
from app import App


class TestTableFormatter(unittest.TestCase):
    """ table formatter unit test """

    def setUp(self):

        self.table = TableFormatter()
        self.test_weather_info = {"Temperature": 35}


    def test_print_out(self):
        """ print_out test """

        printed_out = self.table.print_out(self.test_weather_info, 'Title')
        printable = self.table._make_printable(self.test_weather_info)
        nice_output = self.table._nice_output(printable, 'Title')

        self.assertEqual(printed_out, nice_output)
        self.assertIsInstance(printed_out, str)


    def test_nice_output(self):
        """ _nice_output test """

        output_data = self.table._make_printable(self.test_weather_info)
        nice_output = self.table._nice_output(output_data, 'Title')

        # check return is str
        self.assertIsInstance(nice_output, str)


    def test_make_printable(self):
        """ _make_printable test """

        output_data = self.table._make_printable(self.test_weather_info)

        # check return is list
        self.assertIsInstance(output_data, list)


class TestPlainText(unittest.TestCase):

    def setUp(self):
        self.text = PlainText()
        self.test_weather_info = {"Condition": "Clear and sunny",
                                    "Temperature": 14}

    def test_print_out(self):
        """ test print_out """

        output_text = self.text.print_out(self.test_weather_info, 'Title')

        self.assertIsInstance(output_text, str)


if __name__ == "__main__":
    unittest.main()
