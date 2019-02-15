import unittest

from app import App
import argparse

class TestApp(unittest.TestCase):
    """ Test Case for App """

    def setUp(self):
        self.app = App()
    """
    def test_main(self):
        self.app.main()
        print(dir(self.app.stdout))
    """
    def test_get_logger(self):
        test_logger = self.app._get_logger(self.app.args.verbosity)
        self.assertEqual(str(test_logger), '<Logger app (WARNING)>')
        self.assertEqual(test_logger.name, 'app')
        self.assertEqual(len(test_logger.handlers), 2)

    def test_take_args(self):
        self.assertIsInctance(self.app.args, argparse.ArgumentParser)

    def test_get_option_args(self):
        for provider in ['Accuweather', 'RP5', 'Sinoptik']:
            args = self.app.get_option_args(provider)
            self.assertEqual(str(type(args)), "<class 'list'>")

if __name__ == "__main__":
    unittest.main()
