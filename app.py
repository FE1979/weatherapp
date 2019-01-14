""" Main application """

from html import escape, unescape
import argparse

from providermanager import ProviderManager
from commandmanager import CommandManager
import config
import decorators

class App:

    def __init__(self):
        self.args, self.remaining_args = self.take_args()
        self.providers = ProviderManager()
        self.commands = CommandManager().commands

    def take_args(self):
        """
        Set, parse and manage CLI arguments
        """

        parser = argparse.ArgumentParser(prog="Weatherapp", epilog="Get fun!",
            description="""A program shows you current weather condition in Kyiv
            and, optionaly, temperature forecast""",
            usage="""weatherapp -provider -forecast -csv/-save [file_name]""")

        parser.add_argument("command",
                            help="All - runs specified provider. If not specified runs all switched on",
                            nargs="?")

        parser.add_argument("-csv", metavar="[filename]",
                            help="Export weather info to CSV formatted file",
                            type=str) #App command
        parser.add_argument("-save", metavar="[filename]",
                            help="Saves printed out info into txt file",
                            type=str) #App command
        parser.add_argument("--clear-cache", help="Remove cache files and directory",
                            action="store_true") #App command

        args, remaining_args = parser.parse_known_args()

        print(args)

        return args, remaining_args

    def run_app(self, Provider):
        """
        Runs loading, scraping and printing out weather info depending on given flags
        """

        weather_info = {}

        if Provider.title == 'Accuweather':

            if self.args.loc:
                #define current location of User
                location = []
                print('Your current location:')
                Provider.raw_page = Provider.get_raw_page(Provider.URL) #load forecast
                location = Provider.get_current_location()

                for item in location:
                    print(item, end=" ")
                print('\n') #new line

                location_set = Provider.browse_location() #get new location
                Provider.set_location(location_set) #set location to the Provider
                config.WEATHER_PROVIDERS = config.set_config(Provider.Title,
                                            Provider.get_instance_variables(),
                                            config.WEATHER_PROVIDERS) #save new location to config


            if self.args.next:
                Provider.raw_page = Provider.get_raw_page(Provider.URL_next_day,\
                                            self.args.refresh) #load forecast
                info_next_day = Provider.get_next_day() #run if forecast called
                weather_info.update(info_next_day) #update with forecast

            if not self.args.next:
                Provider.raw_page = Provider.get_raw_page(Provider.URL, \
                                                self.args.refresh) #load a page
                weather_info = Provider.get_info() #extract data from a page
                if self.args.forec:
                    Provider.raw_page = Provider.get_raw_page(Provider.URL_hourly,
                                                self.args.refresh) #load forecast
                    info_hourly = Provider.get_hourly() #run if forecast called
                    weather_info.update(info_hourly) #update with forecast

        elif Provider.title == 'RP5':

            if self.args.loc:
                location = []
                print(f"Your current location:\n{Provider.Location}\n")

                location_set = Provider.browse_location()
                Provider.set_location(location_set) #set location to the config
                config.WEATHER_PROVIDERS = config.set_config(Provider.Title,
                                            Provider.get_instance_variables(),
                                            config.WEATHER_PROVIDERS) #save new location to config


            if self.args.next:
                Provider.raw_page = Provider.get_raw_page(Provider.URL, \
                                                self.args.refresh)
                info_next_day = Provider.get_next_day()
                weather_info.update(info_next_day) #update with forecast

            if not self.args.next:
                Provider.raw_page = Provider.get_raw_page(Provider.URL,\
                                                self.args.refresh) #load a page
                weather_info = Provider.get_info() #extract data from a page
                if self.args.forec:
                    Provider.raw_page = Provider.get_raw_page(Provider.URL) #load forecast
                    info_hourly = Provider.get_hourly() #run if forecast called
                    weather_info.update(info_hourly) #update with forecast

        elif Provider.title == 'Sinoptik':

            if self.args.loc:
                #define current location of User
                location = []
                print(f"Your current location:\n{Provider.Location}\n")

                #set_location_accu()
                location_set = Provider.browse_location()
                Provider.set_location(location_set) #set location to the config
                config.WEATHER_PROVIDERS = config.set_config(Provider.Title,
                                            Provider.get_instance_variables(),
                                            config.WEATHER_PROVIDERS) #save new location to config


            if self.args.next:
                Provider.raw_page = Provider.get_raw_page(Provider.URL,\
                                                            self.args.refresh)
                info_next_day = Provider.get_next_day()
                weather_info.update(info_next_day)

            if not self.args.next:
                Provider.raw_page = Provider.get_raw_page(Provider.URL, \
                                                self.args.refresh) #load a page
                weather_info = Provider.get_info() #extract data from a page
                if self.args.forec:
                    Provider.raw_page = Provider.get_raw_page(Provider.URL,\
                                            self.args.refresh) #load forecast
                    info_hourly = Provider.get_hourly() #run if forecast called
                    weather_info.update(info_hourly) #update with forecast

        try:
            city = Provider.Location
        except KeyError:
            city = ''

        if self.args.next:
            title = Provider.title + ", прогноз на завтра, " + city
        else:
            title = Provider.title + ", поточна погода, " + city

        output_data = self.make_printable(weather_info) #create printable
        self.print_weather(output_data, title) #print weather info on a screen

        """ save loaded data and caching"""

        config.ACTUAL_PRINTABLE_INFO[title] = self.nice_output(output_data, title)

        if self.args.accu:
            config.ACTUAL_WEATHER_INFO['ACCU'] = weather_info
        if self.args.rp5:
            config.ACTUAL_WEATHER_INFO['RP5'] = weather_info
        if self.args.sin:
            config.ACTUAL_WEATHER_INFO['Sinoptik'] = weather_info

        config.save_config(config.CONFIG)

    #@decorators.show_loading
    def main(self):
        weather_info = {}
        title = ''

        command = self.args.command

        if command in self.commands.keys():
            command_factory = self.commands.get(command, None)
            command_factory(self).run()

        if command in self.providers._providers.keys():
            provider = self.providers._providers.get(command)
            weather_info, title = provider(self).run()
            output_data = self.make_printable(weather_info) #create printable
            self.print_weather(output_data, title) #print weather info on a screen

        if not command:
            for title, provider in self.providers._providers.items():
                weather_info, title = provider(self).run()
                output_data = self.make_printable(weather_info) #create printable
                self.print_weather(output_data, title) #print weather info on a screen

        if self.args.clear_cache:
            AnyProvider = self.providermanager._providers['Accuweather']
            AnyProvider.Cache_path = config.WEATHER_PROVIDERS['Accuweather']['Cache_path']
            AnyProvider.clear_cache()
            del AnyProvider
            return None

        if self.args.csv:
            self.save_csv(config.ACTUAL_WEATHER_INFO, args.csv)
        if self.args.save:
            self.save_txt(config.ACTUAL_PRINTABLE_INFO, args.save)

        config.save_config(config.CONFIG)

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

if __name__ == "__main__":
    Ap = App()
    Ap.main()
