import unittest

from managers.commandmanager import CommandManager

class AnyCommand():

    name = "AnyCommand"


class SecondaryCommand():

    name = "SecondaryCommand"

class CommandManagerTest (unittest.TestCase):
    """ Unit tests for CommandManager class """

    def setUp(self):
        self.command_manager = CommandManager()

    def test_load_commands(self):
        """ Test loading commands """

        for item in [AnyCommand, SecondaryCommand]:
            self.command_manager.commands[item.name] = item

        self.assertEqual(len(self.command_manager.commands), 4)
        self.assertTrue('SecondaryCommand' in
                                        self.command_manager.commands.keys())
        self.assertFalse('Any_else_command' in
                                        self.command_manager.commands.keys())

    def test_add(self):
        """ Test Add command """
        self.command_manager.commands['Any_command'] = AnyCommand()

        self.assertTrue('Any_command' in self.command_manager.commands)
        # self.assertEqual(self.command_manager.get('Any_command'), AnyCommand())

    def test_get(self):
        """ Test getting provider by name
        """

        self.assertFalse(
            self.command_manager.commands.get('SecondaryCommand', None)
            )

        self.assertNotEqual(
            self.command_manager.commands.get('ConfigureApp', None).name,
            SecondaryCommand.name
            )

        return


if __name__ == "__main__":
    unittest.main()
