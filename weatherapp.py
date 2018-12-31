"""
Test project
"""

from urllib.request import urlopen, Request
from urllib.parse import quote, unquote
from urllib import parse
from html import escape, unescape
from bs4 import BeautifulSoup
import os
import re
import sys
import time
import pathlib
import hashlib
import argparse
import configparser
import json

import config
import providers

""" Output functions """
def print_weather(output_data, title):
    """
    Prints weather on a screen
    input data - list of two lists: headers and values
    """
    print(nice_output(output_data, title))

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

def save_txt(ACTUAL_PRINTABLE_INFO, filename):
    """ Saves to txt file printable weather info """

    with open(filename+'.txt', 'w') as f:
        for item in ACTUAL_PRINTABLE_INFO:
            f.write(ACTUAL_PRINTABLE_INFO[item])

    pass

""" Main functions """
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
    title = Provider.title

    if args[0].refresh: #if we force page reloading
        force_reload = True
    else:
        force_reload = False


    if title == 'Accuweather':

        if args[0].loc:
            #define current location of User
            location = []
            print('Your current location:')
            Provider.raw_page = Provider.get_raw_page(Provider.url) #load forecast
            location = Provider.get_current_location()

            for item in location:
                print(item, end=" ")
            print('\n') #new line

            location_set = Provider.browse_location() #get new location
            Provider.set_location(location_set) #set location to the config
            config.load_config() #reload config

        if args[0].next:
            Provider.raw_page = Provider.get_raw_page(Provider.url_next_day, force_reload) #load forecast
            info_next_day = Provider.get_next_day() #run if forecast called
            weather_info.update(info_next_day) #update with forecast

        if not args[0].next:
            Provider.raw_page = Provider.get_raw_page(Provider.url, force_reload) #load a page
            weather_info = Provider.get_info() #extract data from a page
            if forec:
                Provider.raw_page = Provider.get_raw_page(Provider.url_hourly, force_reload) #load forecast
                info_hourly = Provider.get_hourly() #run if forecast called
                weather_info.update(info_hourly) #update with forecast

    elif title == 'RP5':

        if args[0].loc:
            location = []
            print(f"Your current location:\n{Provider.location}\n")

            #set_location_accu()
            location_set = Provider.browse_location()
            Provider.set_location(location_set) #set location to the config
            config.load_config() #reload config

        if args[0].next:
            Provider.raw_page = Provider.get_raw_page(Provider.url, force_reload)
            info_next_day = Provider.get_next_day()
            weather_info.update(info_next_day) #update with forecast

        if not args[0].next:
            Provider.raw_page = Provider.get_raw_page(Provider.url, force_reload) #load a page
            weather_info = Provider.get_info() #extract data from a page
            if forec:
                Provider.raw_page = Provider.get_raw_page(Provider.url) #load forecast
                info_hourly = Provider.get_hourly() #run if forecast called
                weather_info.update(info_hourly) #update with forecast

    elif title == 'Sinoptik':

        if args[0].loc:
            #define current location of User
            location = []
            print(f"Your current location:\n{Provider.location}\n")

            #set_location_accu()
            location_set = Provider.browse_location()
            Provider.set_location(location_set) #set location to the config
            config.load_config() #reload config

        if args[0].next:
            Provider.raw_page = Provider.get_raw_page(Provider.url, force_reload)
            info_next_day = Provider.get_next_day()
            weather_info.update(info_next_day)

        if not args[0].next:
            Provider.raw_page = Provider.get_raw_page(Provider.url, force_reload) #load a page
            weather_info = Provider.get_info() #extract data from a page
            if forec:
                Provider.raw_page = Provider.get_raw_page(Provider.url, force_reload) #load forecast
                info_hourly = Provider.get_hourly() #run if forecast called
                weather_info.update(info_hourly) #update with forecast

    try:
        city = Provider.location
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

    pass

def main():

    args = take_args()

    if args.clear_cache:
        clear_cache()
        return None

    if args.u: #sets updating interval
        config.Caching_time = args.u
        config.save_config(config.config)
        return None

    if args.accu:
        Accu = providers.AccuProvider(config.weather_providers['ACCU']['Title'],
                            config.weather_providers['ACCU']['URL'],
                            config.weather_providers['ACCU']['URL_locations'],
                            config.weather_providers['ACCU']['Location'],
                            config.weather_providers['ACCU']['Cache_path'],
                            config.weather_providers['ACCU']['Caching_time'],
                            config.weather_providers['ACCU']['URL_hourly'],
                            config.weather_providers['ACCU']['URL_next_day']
                            )

        run_app(args, Provider=Accu, forec=args.forec)
    if args.rp5:
        RP5 = providers.RP5_Provider(config.weather_providers['RP5']['Title'],
                                config.weather_providers['RP5']['URL'],
                                config.weather_providers['RP5']['URL_locations'],
                                config.weather_providers['RP5']['Location'],
                                config.weather_providers['RP5']['Cache_path'],
                                config.weather_providers['RP5']['Caching_time'],
                                )
        run_app(args, Provider=RP5, forec=args.forec)
    if args.sin:
        Sinoptik = providers.SinoptikProvider(
                                config.weather_providers['Sinoptik']['Title'],
                                config.weather_providers['Sinoptik']['URL'],
                                config.weather_providers['Sinoptik']['URL_locations'],
                                config.weather_providers['Sinoptik']['Location'],
                                config.weather_providers['Sinoptik']['Cache_path'],
                                config.weather_providers['Sinoptik']['Caching_time'],
                                )
        run_app(args, Provider=Sinoptik, forec=args.forec)
    if args.csv:
        save_csv(config.ACTUAL_WEATHER_INFO, args.csv)
    if args.save:
        save_txt(config.ACTUAL_PRINTABLE_INFO, args.save)

    config.save_config(config.config)

if __name__ == "__main__":
    main()
