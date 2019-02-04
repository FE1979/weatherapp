""" Application commands """

from abstract.abstract import Command
import config.config

class ConfigureApp(Command):
    """ Configures application """

    name = 'ConfigureApp'

    def run(self):
        """ Run configuration proccess """
        print('Set providers to show:')
        providers_list = list(enumerate(self.app.providers.get_list()))
        for number, item in providers_list:
            print(f"{number} - {item}")
        print("Enter number of providers separately or S to skip")
        try:
            choice = input('').split()
            #skip

            if 's' or 'S' in choice:
                raise ValueError

            try:
                choice = [int(x) for x in choice]
            except ValueError:
                self.app.logger.error('Only numbers should be entered. Please, restart app and try again.')

            for number, item in providers_list:
                if number in choice:
                    config.PROVIDERS_CONF[providers_list[number][1]]['Show'] = True
                #in case if number is wrong
                elif number < max(choice):
                    continue
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
            self.app.logger.info("Skip")
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
        """ Runs provider configuration proccess"""

        provider_title = ''
        set_loc = False

        choice = input('Do you want set up location? Y/N')

        if choice.lower() == 'y':
            set_loc = True

        if len(self.app.remaining_args) > 0: #if provider is entered by user
            provider_title = self.app.remaining_args[0]

        if provider_title in self.app.providers.get_list(): #if first argument is provider title
            not set_loc and self.set_options(provider_title)
            set_loc and self.set_location(provider_title)
        else: #if no provider chosen do it for all
            for provider_title in self.app.providers.get_list():
                not set_loc and self.set_options(provider_title)
                set_loc and self.set_location(provider_title)

        print('Bye-bye!')

    def set_options(self, provider_title):
        """ sets options for provider """

        for key in config.PROVIDERS_CONF[provider_title]:
            if key == 'Next_day':
                choice = input(f"{provider_title}, show next day forecast? Y/N\n")
                if choice.lower() == 'y':
                    config.PROVIDERS_CONF[provider_title]['Next_day'] = True
                elif choice.lower() == 'n':
                    config.PROVIDERS_CONF[provider_title]['Next_day'] = False
            elif key == 'Next_hours':
                choice = input(f"{provider_title}, show next hours forecast? Y/N\n")
                if choice.lower() == 'y':
                    config.PROVIDERS_CONF[provider_title]['Next_hours'] = True
                if choice.lower() == 'n':
                    config.PROVIDERS_CONF[provider_title]['Next_hours'] = False

    def set_location(self, provider_title):
        """ sets location of provider """

        provider = self.app.providers.get(provider_title)
        provider(self.app).config_location()
