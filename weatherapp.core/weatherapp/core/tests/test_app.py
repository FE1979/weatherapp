import sys

import unittest

from app import App
import argparse

sys.path.insert(0, '..')


class TestApp(unittest.TestCase):
    """ Test Case for App """

    def setUp(self):
        self.app = App()

    def test_get_logger(self):
        """ Test getting logger """

        test_logger = self.app._get_logger(self.app.args.verbosity)
        self.assertEqual(str(test_logger), '<Logger app (WARNING)>')
        self.assertEqual(test_logger.name, 'app')
        self.assertEqual(len(test_logger.handlers), 2)

    def test_take_args(self):
        """ Test taking cli args """

        self.assertIsInstance(self.app.args, argparse.Namespace)

    def test_get_option_args(self):
        """ Test getting options for provider """

        for provider in ['Accuweather', 'RP5', 'Sinoptik']:
            args = self.app.get_option_args(provider)
            self.assertEqual(str(type(args)), "<class 'list'>")

if __name__ == "__main__":
    unittest.main()
