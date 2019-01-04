""" Main application """

from html import escape, unescape
import argparse

class App:

    


    def take_args():
        """
        Set, parse and manage CLI arguments
        """

        parser = argparse.ArgumentParser(prog="Weatherapp", epilog="Get fun!",
            description="""A program shows you current weather condition in Kyiv
            and, optionaly, temperature forecast""",
            usage="""weatherapp -provider -forecast -csv/-save [file_name]""")

        parser.add_argument("-al", "--all", help="Shows weather from all providers",
                            action="store_true", default=True)
        parser.add_argument("-a", "--accu", help="Weather from Accuweather",
                            action="store_true")
        parser.add_argument("-r", "--rp5", help="Weather from RP5",
                            action="store_true")
        parser.add_argument("-s", "--sin", help="Weather from Sinoptik",
                            action="store_true")
        parser.add_argument("-next", help="Next day forecast (ACCU only)",
                            action="store_true")
        parser.add_argument("-loc", help="Browse and set location. ACCU only.",
                            action="store_true")
        group = parser.add_mutually_exclusive_group()
        group.add_argument("-f", "--forec", help="Display forecast for next hours",
                            action="store_true", default=True)
        group.add_argument("-nf", "--noforec", help="Do not display forecast for next hours",
                            action='store_true')
        parser.add_argument("-csv", metavar="[filename]",
                            help="Export weather info to CSV formatted file",
                            type=str)
        parser.add_argument("-save", metavar="[filename]",
                            help="Saves printed out info into txt file",
                            type=str)
        parser.add_argument("-refresh", help="Force reloading pages", action="store_true")
        parser.add_argument("--clear-cache", help="Remove cache files and directory",
                            action="store_true")
        parser.add_argument("-u", metavar="[minutes]",
                            help="Set updating interval in minutes", type=int)

        args = parser.parse_args()

        if args.accu or args.rp5 or args.sin: args.all = False #switch all to False if any of providers called

        if args.all:
            args.accu = args.rp5 = args.sin = True #make all shown

        if args.noforec:
            args.forec = False #set forecast not to show

        return args

    def run_app(*args, Provider, forec):
        """
        Runs loading, scraping and printing out weather info depending on given flags
        """

        weather_info = {}
        title = Provider.Title

        if args[0].refresh: #if we force page reloading
            force_reload = True
        else:
            force_reload = False


        if title == 'Accuweather':

            if args[0].loc:
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


            if args[0].next:
                Provider.raw_page = Provider.get_raw_page(Provider.URL_next_day, force_reload) #load forecast
                info_next_day = Provider.get_next_day() #run if forecast called
                weather_info.update(info_next_day) #update with forecast

            if not args[0].next:
                Provider.raw_page = Provider.get_raw_page(Provider.URL, force_reload) #load a page
                weather_info = Provider.get_info() #extract data from a page
                if forec:
                    Provider.raw_page = Provider.get_raw_page(Provider.URL_hourly, force_reload) #load forecast
                    info_hourly = Provider.get_hourly() #run if forecast called
                    weather_info.update(info_hourly) #update with forecast

        elif title == 'RP5':

            if args[0].loc:
                location = []
                print(f"Your current location:\n{Provider.Location}\n")

                #set_location_accu()
                location_set = Provider.browse_location()
                Provider.set_location(location_set) #set location to the config
                config.WEATHER_PROVIDERS = config.set_config(Provider.Title,
                                            Provider.get_instance_variables(),
                                            config.WEATHER_PROVIDERS) #save new location to config


            if args[0].next:
                Provider.raw_page = Provider.get_raw_page(Provider.URL, force_reload)
                info_next_day = Provider.get_next_day()
                weather_info.update(info_next_day) #update with forecast

            if not args[0].next:
                Provider.raw_page = Provider.get_raw_page(Provider.URL, force_reload) #load a page
                weather_info = Provider.get_info() #extract data from a page
                if forec:
                    Provider.raw_page = Provider.get_raw_page(Provider.URL) #load forecast
                    info_hourly = Provider.get_hourly() #run if forecast called
                    weather_info.update(info_hourly) #update with forecast

        elif title == 'Sinoptik':

            if args[0].loc:
                #define current location of User
                location = []
                print(f"Your current location:\n{Provider.Location}\n")

                #set_location_accu()
                location_set = Provider.browse_location()
                Provider.set_location(location_set) #set location to the config
                config.WEATHER_PROVIDERS = config.set_config(Provider.Title,
                                            Provider.get_instance_variables(),
                                            config.WEATHER_PROVIDERS) #save new location to config


            if args[0].next:
                Provider.raw_page = Provider.get_raw_page(Provider.URL, force_reload)
                info_next_day = Provider.get_next_day()
                weather_info.update(info_next_day)

            if not args[0].next:
                Provider.raw_page = Provider.get_raw_page(Provider.URL, force_reload) #load a page
                weather_info = Provider.get_info() #extract data from a page
                if forec:
                    Provider.raw_page = Provider.get_raw_page(Provider.URL, force_reload) #load forecast
                    info_hourly = Provider.get_hourly() #run if forecast called
                    weather_info.update(info_hourly) #update with forecast

        try:
            city = Provider.Location
        except KeyError:
            city = ''

        if args[0].next:
            title = title + ", прогноз на завтра, " + city
        else:
            title = title + ", поточна погода, " + city

        output_data = make_printable(weather_info) #create printable
        print_weather(output_data, title) #print weather info on a screen

        """ save loaded data and caching"""

        config.ACTUAL_PRINTABLE_INFO[title] = nice_output(output_data, title)

        if args[0].accu:
            config.ACTUAL_WEATHER_INFO['ACCU'] = weather_info
        if args[0].rp5:
            config.ACTUAL_WEATHER_INFO['RP5'] = weather_info
        if args[0].sin:
            config.ACTUAL_WEATHER_INFO['Sinoptik'] = weather_info

        config.save_config(config.CONFIG)

    def main():

        args = take_args()

        if args.clear_cache:
            AnyProvider = providers.WeatherProvider()
            AnyProvider.Cache_path = config.WEATHER_PROVIDERS['ACCU']['Cache_path']
            AnyProvider.clear_cache()
            del AnyProvider
            return None

        if args.u: #sets updating interval
            config.Caching_time = args.u
            config.save_config(config.CONFIG)
            return None

        if args.accu:
            Accu = providers.AccuProvider()
            Accu.initiate(config.WEATHER_PROVIDERS['ACCU'])
            run_app(args, Provider=Accu, forec=args.forec)
        if args.rp5:
            RP5 = providers.RP5_Provider()
            RP5.initiate(config.WEATHER_PROVIDERS['RP5'])
            run_app(args, Provider=RP5, forec=args.forec)
        if args.sin:
            Sinoptik = providers.SinoptikProvider()
            Sinoptik.initiate(config.WEATHER_PROVIDERS['Sinoptik'])
            run_app(args, Provider=Sinoptik, forec=args.forec)
        if args.csv:
            save_csv(config.ACTUAL_WEATHER_INFO, args.csv)
        if args.save:
            save_txt(config.ACTUAL_PRINTABLE_INFO, args.save)

        config.save_config(config.CONFIG)
