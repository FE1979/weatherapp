""" Application commands """

from abstract import Command

class Any(Command):
    """ Command runs turned-on providers """

    name = 'All'

    def run(self):
        """ Runs providers """
        print("I'm running providers")
        print(self.app.providermanager)

class ConfigureApp(Command):
    """ Configures application """

    name = 'ConfigureApp'

    def run(self):
        """ Run configuration proccess """
        print("I configurate application")

class Configure(Command):
    """ Configures Provider """

    name = 'Configure'

    def __init__(self, providers):
        self.providers = providers

    def run(self):
        print("I cofigure Provider")
