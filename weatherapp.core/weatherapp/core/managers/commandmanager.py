""" Application command manager """

from abstract.commands import ConfigureApp, Configure
import abstract.abstract


class CommandManager(abstract.abstract.Manager):
    """ Container for commands """


    def __init__(self):
        self.commands = {}
        self._load_commands()


    def __iter__(self):
        """ Let make it iterable
            :return: command name and instance
            :rtype: tuple
        """
        for key, value in self.commands.items():
            yield key, value


    def _load_commands(self):
        """ Loads commands from commands.py """

        for item in [ConfigureApp, Configure]:
            self.commands[item.name] = item


    def add(self, name, command):
        """ Add command """

        self.commands[name] = command


    def get(self, name):
        """ Get provider by name
            :return: Command instance
            :rtype: command
        """

        return self.commands.get(name, None)
