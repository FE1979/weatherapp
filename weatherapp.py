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

""" Caching """



""" Page loading and scraping functions """


def get_rp5_info(raw_page):
    """ Extracts data from RP5 loaded page
        returns info in dictionary: Temperature, Condition, RealFeel
    """
    weather_info = {}
    soup = BeautifulSoup(raw_page, 'lxml')

    temperature_block = soup.find('div', id = 'ArchTemp') #part with Temperature
    temperature_text = temperature_block.find('span', class_='t_0').string #Actual temperature
    temperature_text = temperature_text[:len(temperature_text) - 3] #remove space and Celsius sign
    weather_info['Temperature'] = int(temperature_text) #make it number

    RealFeel_block = soup.find('table', id='forecastTable_1') #take table with short hourly description
    RealFeel_block = RealFeel_block.find_all('tr') #take all rows
    #find row index with RealFeel
    for item in RealFeel_block:
        id = item.find('a', id="f_temperature")
        if id is None:
            pass
        else:
            index_RF = RealFeel_block.index(item)

    RealFeel_block = list(RealFeel_block)[index_RF].find_all('td') #take all columns in row
    RealFeel_block = list(RealFeel_block)[1] #select 2nd col
    try:
        RF_text = str(list(RealFeel_block.children)[1].get_text()) # and make it string
    except IndexError:
        RF_text = '' #if no data keep it blank
    try:
        weather_info['RealFeel'] = int(RF_text) #make it number
    except ValueError: #if it is blank do keep it
        weather_info['RealFeel'] = ''

    Cond_block = soup.find('table', id='forecastTable_1') #take table with short hourly description
    Cond_block = Cond_block.find_all('tr') #take all rows
    Cond_block = list(Cond_block)[2].find_all('td') #take all columns in 3rd row
    Cond_block = list(Cond_block)[1] #select 2nd col
    Cond_text = str(list(Cond_block.children)[1]) # and make it string

    start_tag = 'b&gt;'
    end_tag = '&lt'
    start = Cond_text.find(start_tag) + len(start_tag) #extract from simple string
    end = Cond_text.find(end_tag, start)
    weather_info['Condition'] = Cond_text[start:end]

    return weather_info

def get_rp5_hourly(raw_page):
    """ Gets temperature forecast for next 8 hours
        Returns dict: Max, Min, Average, Forecast horizon in number of hours
    """

    weather_info = {}
    table_data = []
    soup = BeautifulSoup(raw_page, 'lxml')

    table = soup.find('table', id='forecastTable_1') #get table
    table = table.find_all('tr') #take all rows
    #find row index with Temperature
    for item in table:
        id = item.find('a', id="t_temperature")
        if id is None:
            pass
        else:
            index_T = table.index(item)

    td = list(table)[index_T].find_all('td') #take row with temperature
    for item in td:

        t_0 = item.find('div', class_='t_0') #find div with temperature
        if t_0 is not None: #if there is such div
            t = str(t_0.get_text()) #get text from it
            table_data.append(int(t)) #and append to data

    weather_info['Max'] = max(table_data)
    weather_info['Min'] = min(table_data)
    weather_info['Av'] = sum(table_data) / len(table_data)
    weather_info['Num'] = len(table_data)

    return weather_info

def get_rp5_next_day(raw_page):
    """ Extracts weather info for next day
        returns info in dictionary: Temperature, Condition, RealFeel
        using RegEx
    """
    weather_info = {}

    soup = BeautifulSoup(raw_page, 'lxml')

    forecast = soup.find('div', id="forecastShort-content").get_text() #get string with short forecast
    #Extract forecast: Max, Min temperature and condition
    regex = "Завтра.*\. "
    forecast_start = re.search(regex, forecast) #find starting point of forecast info
    forecast = forecast[forecast_start.start():forecast_start.end()]
    regex = r".\d?\d"
    temperatures_as_str = re.findall(regex, forecast) #find all numbers
    weather_info['Next_day_temp_max'] = int(temperatures_as_str[0]) #First is Max in Celsius
    weather_info['Next_day_temp_min'] = int(temperatures_as_str[1]) #Second is Min in Celsius

    regex = ".*.\d\d .C.F ?, " #all +/-, numbers and C/F signs ended with comma and space
    cond_pos = re.search(regex, forecast) #find start poin of cond description
    forecast = forecast[cond_pos.end():].capitalize() #take a cond string with Capital first letter
    regex = "  +"
    weather_info['Next_day_condition'] = re.sub(regex, '', forecast) #remove spaces

    return weather_info

def get_sinoptik_info(raw_page):
    """ Extracts data from Sinoptik loaded page
        returns info in dictionary: Temperature, Condition, RealFeel
    """
    weather_info = {}

    soup = BeautifulSoup(raw_page, 'html.parser')
    curr_temp_cond = soup.find('div', class_='lSide')
    cond = list(curr_temp_cond.find('div', class_='img').children)
    cond = str(cond[1]['alt'])
    weather_info['Condition'] = cond

    curr_temp = str(curr_temp_cond.find('p', class_='today-temp').get_text())
    weather_info['Temperature'] = int(curr_temp[:-2]) #delete Celsius sign and make number

    curr_realfeel = soup.find('div', class_='rSide')
    curr_realfeel = curr_realfeel.find('tr', class_='temperatureSens')
    curr_realfeel = str(curr_realfeel.find('td', class_='p1').get_text())
    weather_info['RealFeel'] = int(curr_realfeel[:-1]) #remove grade sign and make number

    return weather_info

def get_sinoptik_hourly(raw_page):
    """ Gets temperature forecast for next 8 hours
        Returns dict: Max, Min, Average, Forecast horizon in number of hours
    """

    weather_info = {}
    table_data = []

    soup = BeautifulSoup(raw_page, 'html.parser')
    table = soup.find('table', class_='weatherDetails')
    table = table.find('tr', class_='temperature')
    table = table.find_all('td')

    for item in list(table):
        t = item.get_text()
        table_data.append(int(t[:-1])) #remove grade sign

    weather_info['Max'] = max(table_data)
    weather_info['Min'] = min(table_data)
    weather_info['Av'] = sum(table_data) / len(table_data)
    weather_info['Num'] = len(table_data)

    return weather_info

def get_sinoptik_next_day(raw_page):
    """ Extracts weather info for next day
        returns info in dictionary: Temperature, Condition, RealFeel
    """
    weather_info = {}

    soup = BeautifulSoup(raw_page, 'html.parser')
    next_day_block = soup.find('div', id="bd2")
    regex = "weatherIco.*" #there is different weather icons for condition
    next_day_cond = next_day_block.find('div', class_=re.compile(regex))
    weather_info['Next_day_condition'] = str(next_day_cond.attrs['title'])
    #find max temperature
    Next_day_temp = next_day_block.find('div', class_="max")
    Next_day_temp = Next_day_temp.find('span').string
    weather_info['Next_day_temp_max'] = int(Next_day_temp[:-1])
    #Find min temp
    Next_day_temp = next_day_block.find('div', class_="min")
    Next_day_temp = Next_day_temp.find('span').string
    weather_info['Next_day_temp_min'] = int(Next_day_temp[:-1])

    return weather_info

""" Location functions """

def browse_location_sinoptik(level = 0, URL_location = config.weather_providers['Sinoptik']['URL_locations']):
    """ Browse recursively locations of Sinoptik
        Starts from continents
        defaults: level = 0: continent level
                  URL_location: page with continents, Europe by default
        Each next call with new URL and level + 1
        Returns: URL (current weather), name of Location
    """

    levels = ['continent', 'country', 'region', 'city'] #for user input and level check
    raw_page = get_raw_page(URL_location) #read locations
    locations_list = {} #locations associated with their urls
    location_set = {} #result of func

    if level == 0: #continents and countries are on same page so if we are on 0 level we should print continents
        soup = BeautifulSoup(raw_page, 'html.parser') #parse page
        raw_list = soup.find('div', class_="mapRightCol") #find list of locations
        raw_list = raw_list.find('div') #take first div
        raw_list = raw_list.find_all('a') #take all links in list of locations

        for item in raw_list: #associate location with ulr
            url_decoded = quote(item.attrs['href'])
            locations_list[item.get_text()] = "https:" + url_decoded

        for item in locations_list: #print out locations
            print(item)

    if level == 1 or level == 2: #if country or region level
        soup = BeautifulSoup(raw_page, 'html.parser') #parse page
        raw_list = soup.find('div', class_="maxHeight") #find list of locations

        raw_list = raw_list.find('div') #take first div
        raw_list = raw_list.find_all('a') #take all links in list of locations

        for item in raw_list: #associate location with ulr
            url_decoded = quote(item.attrs['href'])
            locations_list[item.get_text()] = "https:" + url_decoded

        for item in locations_list: #print out locations
            print(item)

    if level == 3: #if city level
        soup = BeautifulSoup(raw_page, 'html.parser') #parse page
        raw_list = soup.find('div', class_="mapBotCol") #find list of locations
        raw_list = raw_list.find('div', class_="clearfix")
        raw_list = raw_list.find_all('a') #take all links in list of locations
        print(raw_list)
        for item in raw_list: #associate location with ulr
            url_decoded = quote(item.attrs['href'])
            locations_list[item.get_text()] = "https:" + url_decoded

        for item in locations_list: #print out locations
            print(item)

    choice = input(f"\nEnter {levels[level]} name:\n") #user input

    if level != 3:
        #call this function again with new locations

        location_set = browse_location_sinoptik(level+1, locations_list[choice])

    if level == 3:
        location_set['URL'] = locations_list[choice]
        location_set['Location'] = choice

    return location_set

def set_location_Sinoptik(location_set):
    """ Sets Sinoptik location to the config """

    weather_providers['Sinoptik']['URL'] = location_set['URL']
    weather_providers['Sinoptik']['Location'] = location_set['Location']

    save_config(config)

def browse_location_rp5(level = 0, URL_location = config.weather_providers['RP5']['URL_locations'] ):
    """ Browse recursively locations of RP5
        Starts from all countries
        defaults: level = 0: country level
                  URL_location: page with countries
        Each next call with new URL and level + 1
        Returns: URL (current weather), name of Location
    """

    levels = ['country', 'region', 'city'] #for user input and level check
    location_set = {}
    locations_list = {} #locations associated with their urls
    raw_page = get_raw_page(URL_location) #read locations

    soup = BeautifulSoup(raw_page, 'lxml') #parse page
    table = soup.find('div', class_="countryMap") #find table

    if level == 0: #it only exists on country level
        links = table.find_all('div', class_="country_map_links") #get all links

        for item in links:
            link = item.find('a') #extract urls
            url_decoded = quote(link.attrs['href']) #decode
            locations_list[link.get_text()] = "http://rp5.ua" + url_decoded #sve to the table

        for item in locations_list: #print out locations
            print(item)

    if level == 1:
        links = table.find_all('a', class_='href12') #get all links

        for item in links:
            url_decoded = quote(item.attrs['href']) #decode
            locations_list[item.attrs['title']] = "http://rp5.ua/" + url_decoded #sve to the table

        for item in locations_list: #print out locations
            print(item)

    if level == 2:
        links = table.find_all('a') #get all links

        for item in links:
            url_decoded = quote(item.attrs['href']) #decode
            locations_list[item.get_text()] = "http://rp5.ua/" + url_decoded #sve to the table

        for item in locations_list: #print out locations
            print(item)

    choice = input(f"\nEnter {levels[level]} name:\n") #user input

    if level <2: #if not city level
        location_set = browse_location_rp5(level+1, locations_list[choice])

    if level == 2: #final if city level
        location_set['URL'] = locations_list[choice]
        location_set['Location'] = choice

    return location_set

def set_location_rp5(location_set):
    """ Sets RP5 location to the config """

    weather_providers['RP5']['URL'] = location_set['URL']
    weather_providers['RP5']['Location'] = location_set['Location']

    save_config(config)

def search_location_rp5():
    """ Searches location typed by user through RP5 """

    location_search = input("Type location to search\n")
    data = location_search.encode('utf-8')

    URL_search = weather_providers['RP5']['URL_search']
    HEAD_search = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:63.0) Gecko/201'}
    SEARCH_REQUEST = Request(URL_search, data = data, headers = HEAD_search)
    PAGE_SEARCH = urlopen(SEARCH_REQUEST).read()
    PAGE_SEARCH = str(PAGE_SEARCH, encoding = 'utf-8')

    print(PAGE_SEARCH)

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
    URL = Provider.url
    try:
        URL_hourly = Provider.url_hourly
    except KeyError:
        URL_hourly = Provider.url
    try:
        URL_next_day = Provider.url_next_day
    except KeyError:
        URL_hourly = Provider.url

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
            print(f"Your current location:\n{weather_providers['RP5']['Location']}\n")

            #set_location_accu()
            location_set = browse_location_rp5()
            set_location_rp5(location_set) #set location to the config
            load_config() #reload config

        if args[0].next:
            raw_page = get_raw_page(URL_next_day, force_reload)
            info_next_day = get_rp5_next_day(raw_page)
            weather_info.update(info_next_day) #update with forecast

        if not args[0].next:
            raw_page = get_raw_page(URL, force_reload) #load a page
            weather_info = get_rp5_info(raw_page) #extract data from a page
            if forec:
                raw_page = get_raw_page(URL_hourly) #load forecast
                info_hourly = get_rp5_hourly(raw_page) #run if forecast called
                weather_info.update(info_hourly) #update with forecast

    elif title == 'Sinoptik':

        if args[0].loc:
            #define current location of User
            location = []
            print(f"Your current location:\n{weather_providers['Sinoptik']['Location']}\n")

            #set_location_accu()
            location_set = browse_location_sinoptik()
            set_location_Sinoptik(location_set) #set location to the config
            load_config() #reload config

        if args[0].next:
            raw_page = get_raw_page(URL_next_day, force_reload)
            info_next_day = get_sinoptik_next_day(raw_page)
            weather_info.update(info_next_day)

        if not args[0].next:
            raw_page = get_raw_page(URL, force_reload) #load a page
            weather_info = get_sinoptik_info(raw_page) #extract data from a page
            if forec:
                raw_page = get_raw_page(URL_hourly, force_reload) #load forecast
                info_hourly = get_sinoptik_hourly(raw_page) #run if forecast called
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
                                    config.weather_providers['ACCU']['URL_next_day'])

        run_app(args, Provider=Accu, forec=args.forec)
    if args.rp5:
        run_app(args, provider=config.weather_providers['RP5'], forec=args.forec)
    if args.sin:
        run_app(args, provider=config.weather_providers['Sinoptik'], forec=args.forec)
    if args.csv:
        save_csv(config.ACTUAL_WEATHER_INFO, args.csv)
    if args.save:
        save_txt(config.ACTUAL_PRINTABLE_INFO, args.save)

    config.save_config(config.config)

if __name__ == "__main__":
    main()
