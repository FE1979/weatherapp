""" Main application """

import argparse
import pathlib
import sys
import traceback
import logging

import config.decorators
from config import config
from managers.providermanager import ProviderManager
from managers.commandmanager import CommandManager
import managers.formatters as formatters

class App:

    def __init__(self):
        self.args, self.remaining_args = self.take_args()
        self.providers = ProviderManager()
        self.commands = CommandManager().commands
        self.logger = self._get_logger(self.args.verbosity)
        self.stdin = sys.stdin
        self.stdout = sys.stdout
        self.stderr = sys.stderr
        self.formatter = None

        #define the displaying way of weather data
        if self.args.d:
            self.formatter = formatters.get_formatter(self.args.d)
        if self.formatter == None or not self.args.d: #if wrong display type or no argument entered read the config
            self.formatter = formatters.get_formatter(config.WEATHER_PROVIDERS['App']['Display'])

    @staticmethod
    def _get_logger(verbose_lvl):
        """ Gets looger forr application """

        logger = logging.getLogger('app')
        console = logging.StreamHandler()

        if verbose_lvl == 1:
            logger.setLevel(logging.INFO)
            console.setLevel(logging.INFO)
        elif verbose_lvl == 2:
            logger.setLevel(logging.DEBUG)
            console.setLevel(logging.DEBUG)
        else:
            logger.setLevel(logging.WARNING)
            console.setLevel(logging.WARNING)

        fmt = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)s')
        console.setFormatter(fmt)
        logger.addHandler(console)

        return logger

    def take_args(self):
        """
        Set, parse and manage CLI arguments
        """

        parser = argparse.ArgumentParser(prog="Weatherapp", epilog="Get fun!",
            formatter_class = argparse.RawTextHelpFormatter,
            description="""A program shows you current weather condition and, optionaly, temperature forecast.\n
            Provider options:
            -f, --forec: displays forecast for next hours
            -nf, --noforec: do not display forecast for next hours
            -refresh: force reloading pages""",
            usage="""app command / provider -forecast -csv/-save [file_name]""")

        parser.add_argument("command",
            help="""ConfigureApp - aplication configuration.
Configure - provider configuration.
Provider - show specified provider.""",
            nargs="?")

        parser.add_argument("-d", metavar="[display type]", help="""Define way of displaying results:
type 'table' - as table, 'plain' - as plain text""", type=str)
        parser.add_argument("-csv", metavar="[filename]",
                            help="Export weather info to CSV formatted file",
                            type=str) #App command
        parser.add_argument("-save", metavar="[filename]",
                            help="Saves printed out info into txt file",
                            type=str) #App command
        parser.add_argument("--clear-cache", help="Remove cache files and directory",
                            action="store_true") #App command
        parser.add_argument("--debug", help="Show error tracebacks",
                            action="store_true")
        parser.add_argument("-v", "--verbosity", help="Debug level, -v - INFO, -vv - DEBUG, -vvv - WARNING",
                            action="count")

        args, remaining_args = parser.parse_known_args()

        return args, remaining_args

    def get_option_args(self, provider_title):
        """ Loads show options from providers config
            if no options defined by user
        """
        args = []
        options = config.PROVIDERS_CONF[provider_title] #get options for provider
        for item in options:
            if item == 'Next_day' and options[item]: #if Next_day == True
                args.append('-next') #set CLI argument
            elif item == 'Next_hours' and options[item]:
                args.append('-f')

        return args

    @staticmethod
    def clear_cache():
        """ Removes cache directory """

        path = pathlib.Path(config.WEATHER_PROVIDERS['App']['Cache_path'])

        answer = input('Do you really want to remove all cache files with directory? Y/N\n')
        if answer.lower() == 'y':
            for item in list(path.glob('*.*')):
                item.unlink()
            self.stdout.write('Files removed')
            path.rmdir()
            self.stdout.write('Directory removed')
        else:
            pass


    @staticmethod
    def save_csv(ACTUAL_WEATHER_INFO, filename):
        """ Saves weather info into comma-separated file
        with two columns: head, data
        new entry separated by new line sign"""
        write_line = '' #container for writing a line in file
        with open(filename+'.csv', 'w') as f:
            for item in ACTUAL_WEATHER_INFO:
                write_line = item +', ,\n' #header for next provider
                f.write(write_line)
                for item_data in ACTUAL_WEATHER_INFO[item]:
                    write_line = item_data + ',' + \
                    str(ACTUAL_WEATHER_INFO[item][item_data]) + '\n' #row head and data
                    f.write(write_line)
        pass

    def save_txt(self, ACTUAL_PRINTABLE_INFO, filename):
        """ Saves to txt file printable weather info """

        self.stdout = open(filename+'.txt', 'w')
        for line in ACTUAL_PRINTABLE_INFO:
            self.stdout.write(f"{ACTUAL_PRINTABLE_INFO[line]}\n")
        self.stdout.close()

        pass

    def produce_output(self, weather_info, title):
        """ Produces outputs to the screen and to config vars for file saving """

        self.stdout.write(self.formatter.print_out(weather_info, title))
        config.ACTUAL_WEATHER_INFO[title] = weather_info
        config.ACTUAL_PRINTABLE_INFO[title] = self.formatter.print_out(weather_info,
                                                                            title)

    #@decorators.show_loading
    def main(self):
        weather_info = {}
        title = ''
        get_options = False

        #clear cache first and exit. If no such option - continue
        if self.args.clear_cache:
            self.clear_cache()
            return None

        # check if config file is valid, exit if not
        if not config.is_valid():
            self.stdout.write('Config files are broken. Delete them to reconfigure to defaults')
            return

        if len(self.remaining_args) == 0: #get options if no CLI provider args
            get_options = True

        command = self.args.command

        if command in self.commands.keys():
            command_factory = self.commands.get(command)
            command_factory(self).run()

        elif command in self.providers.get_list():
            if get_options: #get options if no CLI provider args
                self.remaining_args = self.get_option_args(command)
            provider = self.providers.get(command)
            weather_info, title = provider(self).run()
            self.produce_output(weather_info, title)

        elif not command: #run all providers if 'Show' option is set
            for item in config.PROVIDERS_CONF:
                if get_options: #get options if no CLI provider args
                    self.remaining_args = self.get_option_args(item)

                if config.PROVIDERS_CONF[item]['Show'] == True:
                    provider = self.providers.get(item)
                    weather_info, title = provider(self).run()
                    self.produce_output(weather_info, title)

        else:
            self.stdout.write('No such command')

        if self.args.csv:
            self.save_csv(config.ACTUAL_WEATHER_INFO, self.args.csv)

        if self.args.save:
            self.save_txt(config.ACTUAL_PRINTABLE_INFO, self.args.save)

        config.save_config(config.CONFIG)
        config.write_providers_conf()


if __name__ == "__main__":
    Ap = App()
    try:
        Ap.main()
    except Exception:
        if Ap.args.debug:
            Ap.logger.exception('Unexpected error')
        else:
            Ap.logger.error(f'Unexpected error, {sys.exc_info()[0]}')
        sys.exit()
