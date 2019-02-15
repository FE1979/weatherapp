""" Application commands
    ConfigureApp: set provider to show, caching time and way of app output
    Configure: set Provider options
"""

from abstract.abstract import Command
import config.config as config


class ConfigureApp(Command):
    """ Configures application
        Options to configure:
        - what provider application should call
        - set caching time
        - type of weather information output
    """

    name = 'ConfigureApp'

    def run(self):
        """ Run configuration proccess """

        self.app.stdout.write('Set providers to show:\n')
        providers_list = list(enumerate(self.app.providers.get_list()))
        for number, item in providers_list:
            self.app.stdout.write(f"{number} - {item}\n")
        self.app.stdout.write(
                        "Enter number of providers separately or S to skip\n"
                        )
        try:
            choice = input('').split()

            if ('s' or 'S') in choice:  # skip
                raise ValueError

            try:
                choice = [int(x) for x in choice]
            except ValueError:
                self.app.logger.error(
                    'Only numbers should be entered. '
                    'Please, restart app and try again.')

            for number, item in providers_list:
                if number in choice:
                    config.PROVIDERS_CONF[providers_list[number][1]]['Show'] =
                    True

                elif number not in choice:
                    config.PROVIDERS_CONF[providers_list[number][1]]['Show'] =
                    False

                elif number < max(choice):  # in case if number is wrong
                    continue

        except ValueError:
            pass

        self.app.stdout.write(
            'Do you want to set refresh time for all providers?\n')
        reload_time = input('Type time in minutes or any non-number to skip\n')

        """ if user entered non-number - quit
            in other case set refresh time for all providers """
        try:
            reload_time = int(reload_time)
            for item in config.WEATHER_PROVIDERS:
                for key in config.WEATHER_PROVIDERS[item]:
                    if key == 'Caching_time':
                        config.WEATHER_PROVIDERS[item][key] = reload_time
        except ValueError:
            self.app.logger.info("Skip")

        display_option = input(
            "Type '1' for displaying weather " +
            "info as a table or '2' - as plain text?\n")
        if display_option == '1':
            config.WEATHER_PROVIDERS['App']['Display'] = 'table'
        elif display_option == '2':
            config.WEATHER_PROVIDERS['App']['Display'] = 'plain'

        print(config.PROVIDERS_CONF)


class Configure(Command):
    """ Configures Provider
        Options:
        - location
        - next day forecast
        - hourly forecast
    """

    name = 'Configure'

    def run(self):
        """ Runs provider configuration proccess
            If Provider noted in CLI - configure it
            Configure all Providers if no CLI argument
            Function calls set_options to set forecast options
        """

        provider_title = ''
        set_loc = False

        choice = input('Do you want set up location? Y/N\n')

        if choice.lower() == 'y':
            set_loc = True

        if len(self.app.remaining_args) > 0:  # if provider is entered by user
            provider_title = self.app.remaining_args[0]

        # run for noted Provider if first argument is provider title
        if provider_title in self.app.providers.get_list():
            not set_loc and self.set_options(provider_title)
            set_loc and self.set_location(provider_title)

        # do it for all if no provider chosen
        else:
            for provider_title in self.app.providers.get_list():
                not set_loc and self.set_options(provider_title)
                set_loc and self.set_location(provider_title)

        self.app.stdout.write('Bye-bye!')

    def set_options(self, provider_title):
        """ Sets options for provider
            :param provider_title: Provider title
        """

        for key in config.PROVIDERS_CONF[provider_title]:
            if key == 'Next_day':
                choice = input(f"{provider_title}, " +
                                "show next day forecast? Y/N\n")
                if choice.lower() == 'y':
                    config.PROVIDERS_CONF[provider_title]['Next_day'] = True
                elif choice.lower() == 'n':
                    config.PROVIDERS_CONF[provider_title]['Next_day'] = False
            elif key == 'Next_hours':
                choice = input(f"{provider_title}, " +
                                "show next hours forecast? Y/N\n")
                if choice.lower() == 'y':
                    config.PROVIDERS_CONF[provider_title]['Next_hours'] = True
                if choice.lower() == 'n':
                    config.PROVIDERS_CONF[provider_title]['Next_hours'] = False

    def set_location(self, provider_title):
        """ Sets location of provider
            :param provider_title: Provider title
        """

        provider = self.app.providers.get(provider_title)
        provider(self.app).config_location()
