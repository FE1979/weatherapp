""" Main application """

from html import escape, unescape
import argparse
import pathlib

from providermanager import ProviderManager
from commandmanager import CommandManager
import sys
import traceback
import config
import logging
import decorators

class App:

    def __init__(self):
        self.args, self.remaining_args = self.take_args()
        self.providers = ProviderManager()
        self.commands = CommandManager().commands
        self.logger = self._get_logger(self.args.verbosity)

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
            print('Config files are broken. Delete them to reconfigure to defaults')
            return

        if len(self.remaining_args) == 0: #get options if no CLI provider args
            get_options = True

        command = self.args.command

        if command in self.commands.keys():
            command_factory = self.commands.get(command)
            command_factory(self).run()

        if command in self.providers.get_list():
            if get_options: #get options if no CLI provider args
                self.remaining_args = self.get_option_args(command)
            provider = self.providers.get(command)
            weather_info, title = provider(self).run()
            output_data = self.make_printable(weather_info) #create printable
            self.print_weather(output_data, title) #print weather info on a screen

            config.ACTUAL_WEATHER_INFO[provider.title] = weather_info
            config.ACTUAL_PRINTABLE_INFO[title] = self.nice_output(output_data,
                                                                    title)

        if not command:
            for item in config.PROVIDERS_CONF:
                if get_options: #get options if no CLI provider args
                    self.remaining_args = self.get_option_args(item)

                if config.PROVIDERS_CONF[item]['Show'] == True:
                    provider = self.providers.get(item)
                    weather_info, title = provider(self).run()
                    output_data = self.make_printable(weather_info) #create printable
                    self.print_weather(output_data, title) #print weather info on a screen

                    config.ACTUAL_WEATHER_INFO[provider.title] = weather_info
                    config.ACTUAL_PRINTABLE_INFO[title] = self.nice_output(output_data,
                                                                        title)
        else:
            print('No such command')

        if self.args.csv:
            self.save_csv(config.ACTUAL_WEATHER_INFO, self.args.csv)
            print(config.ACTUAL_WEATHER_INFO)
        if self.args.save:
            self.save_txt(config.ACTUAL_PRINTABLE_INFO, self.args.save)

        config.save_config(config.CONFIG)
        config.write_providers_conf()

    """ Output functions """

    def print_weather(self, output_data, title):
        """
        Prints weather on a screen
        input data - list of two lists: headers and values
        """
        print(self.nice_output(output_data, title))

    @staticmethod
    def nice_output(table_data, title):
        """ This forms nice table output for printing or saving to the file
        Replaced old create_table
        """

        nice_txt = ''
        first_column_len = len(max(table_data[0], key = lambda item: len(item))) + 2
        second_column_len = len(max(table_data[1], key = lambda item: len(item))) + 2
        header_len = len(title)

        if header_len > first_column_len + second_column_len:
            second_column_len = header_len - first_column_len

        width = first_column_len + second_column_len + 1
        counter = len(table_data[0])
        i = 0

        #print top of table with title
        nice_txt = '+' + '-'*(width) + '+' + '\n'
        nice_txt = nice_txt + '|' + title.center(width, ' ') + '|' + '\n'
        nice_txt = nice_txt +'+' + '-'*(first_column_len) \
                            + '+' + '-'*(second_column_len) + '+' + '\n'

        while i < counter: #print out headers and values
            nice_txt = nice_txt \
                + '| ' + str(table_data[0][i]).ljust(first_column_len-1, ' ')
            nice_txt = nice_txt \
                + '| ' + str(table_data[1][i]).ljust(second_column_len-1, ' ') + '|'
            nice_txt = nice_txt + '\n'
            i += 1
            pass
        #bottom line
        nice_txt = nice_txt \
                + '+' + '-'*(first_column_len) + '+' + '-'*(second_column_len) + '+'
        #separation blank line
        nice_txt = nice_txt + '\n'

        return nice_txt

    @staticmethod
    def make_printable(weather_info):
        """ Transform weather data to printable format
            headers_dict - translation dictionary
            temperature_heads - to insert Celsius sign if needed
            print_order - to define which way weather_info will show
        """
        headers_dict = {'Temperature': 'Температура',
                        'RealFeel': 'Відчувається як',
                        'Condition': 'На небі',
                        'Max': 'Максимальна', 'Min': 'Мінімальна', 'Av': 'Середня',
                        'Num': 'Прогноз на, годин',
                        'Deg': f"{unescape('&deg')}C",
                        'Next_day_temp': 'Максимальна вдень',
                        'Next_day_temp_max': 'Максимальна вдень', #for RP5
                        'Next_day_temp_min': 'Мінімальна вдень', #for RP5
                        'Next_day_RF': 'Відчуватиметься вдень як',
                        'Next_day_condition': 'На небі вдень буде',
                        'Next_night_temp': 'Мінімальна вночі',
                        'Next_night_RF': 'Відчуватиметься вночі як',
                        'Next_night_condition': 'На небі вночі буде'}
        temperature_heads = ['Temperature', 'RealFeel', 'Max', 'Min', 'Av',
                            'Next_day_temp', 'Next_day_RF', 'Next_night_temp',
                            'Next_night_RF', 'Next_day_temp_max', 'Next_day_temp_min']
        print_order = ['Temperature', 'RealFeel', 'Condition', 'Num', 'Max', 'Min', 'Av',
                        'Next_day_temp', 'Next_day_temp_max', 'Next_day_temp_min',
                        'Next_day_RF', 'Next_day_condition',
                        'Next_night_temp', 'Next_night_RF', 'Next_night_condition']
        output_data = [[],[]]

        for item in print_order: #in printing order
            if item in weather_info.keys(): #if there is a data
                if item in temperature_heads: #if we need to show Celsius
                    output_data[0].append(headers_dict[item])
                    if weather_info[item] != '': #if temp is not blank
                        output_data[1].append(f"{weather_info[item]:.0f}" + ' ' + headers_dict['Deg'])
                    else:
                        output_data[1].append(f"{weather_info[item]}" + ' ' + headers_dict['Deg'])
                else:
                    output_data[0].append(headers_dict[item])
                    output_data[1].append(str(weather_info[item]))
            else:
                pass

        return output_data

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

    @staticmethod
    def save_txt(ACTUAL_PRINTABLE_INFO, filename):
        """ Saves to txt file printable weather info """

        with open(filename+'.txt', 'w') as f:
            for item in ACTUAL_PRINTABLE_INFO:
                f.write(ACTUAL_PRINTABLE_INFO[item])

        pass

    @staticmethod
    def clear_cache():
        """ Removes cache directory """

        path = pathlib.Path(config.WEATHER_PROVIDERS['App']['Cache_path'])

        answer = input('Do you really want to remove all cache files with directory? Y/N\n')
        if answer.lower() == 'y':
            for item in list(path.glob('*.*')):
                item.unlink()
            print('Files removed')
            path.rmdir()
            print('Directory removed')
        else:
            pass

if __name__ == "__main__":
    Ap = App()
    try:
        Ap.main()
    except Exception:
        if Ap.args.debug:
            traceback.print_exc()
        else:
            print('Unexpected error', sys.exc_info()[0])
        sys.exit()
