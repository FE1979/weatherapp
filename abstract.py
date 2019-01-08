""" Abstract classes for weatherapp project """

import abc
import argparse

class Command(abc.ABC):
    """ Base class for commands """

    def __init__(self, app):
        self.app = app

    @staticmethod
    def get_parser():
        parser = parser.ArgumentParser()
        return parser

    @abc.abstractmethod
    def run(self, argv):
        """ I don't understand it's purpose, just copiyng
            Let it be
            Should be overriden
        """
