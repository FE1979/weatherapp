""" Application commands """

from abstract import Command

import config

class ConfigureApp(Command):
    """ Configures application """

    name = 'ConfigureApp'

    def run(self):
        """ Run configuration proccess """
        print('Set providers to show:')
        providers_list = list(enumerate(self.app.providers._providers.keys()))
        for number, item in providers_list:
            print(f"{number} - {item}")
        print("Enter number of providers separately or S to skip")
        try:
            choice = input('').split()
            choice = [int(x) for x in choice]

            for number, item in providers_list:
                if number in choice:
                    config.PROVIDERS_CONF[providers_list[number][1]]['Show'] = True
                else:
                    config.PROVIDERS_CONF[providers_list[number][1]]['Show'] = False
        except ValueError:
            pass

        print('Do you want to set refresh time for all providers?')
        reload_time = input('Type time in minutes or any non-number to skip\n')

        #if user enter non-number - quit
        try:
            reload_time = int(reload_time)
        except ValueError:
            return
        #set refresh time for all providers
        for item in config.WEATHER_PROVIDERS:
            for key in config.WEATHER_PROVIDERS[item]:
                if key == 'Caching_time':
                    config.WEATHER_PROVIDERS[item][key] = reload_time

class Configure(Command):
    """ Configures Provider """

    name = 'Configure'

    def run(self):
        for item in self.app.providers._providers:
            for key in config.PROVIDERS_CONF[item]:
                if key == 'Next_day':
                    choice = input(f"{item}, show next day forecast? Y/N\n")
                    if choice.lower() == 'y':
                        config.PROVIDERS_CONF[item]['Next_day'] = True
                elif key == 'Next_hours':
                    choice = input(f"{item}, show next hours forecast? Y/N\n")
                    if choice.lower() == 'y':
                        config.PROVIDERS_CONF[item]['Next_hours'] = True
        print('Bye-bye!')
