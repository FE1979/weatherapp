""" Application command manager """

from commands import ConfigureApp, Configure

class CommandManager:
    """ Container for commands """

    def __init__(self):
        self.commands = {}
        self._load_commands()

    def _load_commands(self):
        """ Loads commands from commands.py """

        for item in [ConfigureApp, Configure]:
            self.commands[item.name] = item
