"""
Test project
"""

from urllib.request import urlopen, Request
from html import escape, unescape
from bs4 import BeautifulSoup
import re
import sys
import argparse



""" Define global params """
weather_providers = {
'ACCU': {'Title': 'Accuweather',
        'URL': "https://www.accuweather.com/uk/ua/kyiv/324505/weather-forecast/324505",
        'URL_hourly': "https://www.accuweather.com/uk/ua/kyiv/324505/hourly-weather-forecast/324505",
        'URL_next_day': "https://www.accuweather.com/uk/ua/kyiv/324505/daily-weather-forecast/324505?day=2",
        'URL_regions': "https://www.accuweather.com/uk/browse-locations"
        },
'RP5': {'Title': 'RP5',
        'URL': "http://rp5.ua/%D0%9F%D0%BE%D0%B3%D0%BE%D0%B4%D0%B0_%D0%B2_%D0%9A%D0%B8%D1%94%D0%B2%D1%96",
        },
'Sinoptik': {'Title': 'Sinoptik',
        'URL': "https://ua.sinoptik.ua/%D0%BF%D0%BE%D0%B3%D0%BE%D0%B4%D0%B0-%D0%BA%D0%B8%D1%97%D0%B2",
        }
}

ACTUAL_WEATHER_INFO = {}
ACTUAL_PRINTABLE_INFO = {}

""" End of global params """

""" Page loading and scraping functions """
def get_raw_page(URL):
    """
    Loads a page from given URL
    """
    HEAD = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:63.0) Gecko/201'}
    INFO_REQUEST = Request(URL, headers = HEAD)
    PAGE = urlopen(INFO_REQUEST).read()
    PAGE = str(PAGE, encoding = 'utf-8')

    return PAGE

def get_accu_info(raw_page):
    """ Extracts weather info from ACCUWEATHER loaded page using BS4
        returns info in dictionary: Temperature, Condition, RealFeel
    """
    weather_info = {}

    soup = BeautifulSoup(raw_page, 'html.parser')

    current_cond_div = soup.find('div', id='feed-tabs', class_='panel-list cityforecast') #find block with curr condition
    weather_info['Temperature'] = str(current_cond_div.find('span', class_='large-temp').string) #temperature and convert it to string type
    weather_info['Temperature'] = int(weather_info['Temperature'][:-1]) #remove grade sign, make it number
    weather_info['Condition'] = str(current_cond_div.find('span', class_='cond').string) #condition
    RealFeel = str(current_cond_div.find('span', class_='realfeel').string) #RealFeel
    weather_info['RealFeel'] = int(RealFeel[10:-1]) #remove word 'RealFeel' from it and grade sign. make it number

    return weather_info

def get_accu_hourly(raw_page):
    """ Gets temperature forecast for next 8 hours
        Returns dict: Max, Min, Average, Forecast horizon in number of hours
    """

    weather_info = {}
    soup = BeautifulSoup(raw_page, 'html.parser')

    hourly_data = soup.find('div', class_='hourly-table overview-hourly') #find hourly forecast table
    hourly_data = hourly_data.select('tbody tr span') #extract only <span> with data

    i=0
    hourly_temperature = []
    while i<8: #move 8 times (8 hours forecast)
        hourly_temperature.append(int(list(hourly_data)[i].string[:-1]))
        i += 1
        pass
    weather_info['Max'] = max(hourly_temperature)
    weather_info['Min'] = min(hourly_temperature)
    weather_info['Av'] = sum(hourly_temperature) / len(hourly_temperature)
    weather_info['Num'] = len(hourly_temperature)

    return weather_info

def get_accu_next_day(raw_page):
    """ Extracts weather info for next day
        returns info in dictionary: Temperature, Condition, RealFeel
    """
    weather_info = {}
    regex = "  1?" #to remove unnessecary symbols

    soup = BeautifulSoup(raw_page, 'html.parser')

    next_day_forec = soup.find('div', id="detail-day-night") #find dey/night forecast panel
    day_forec = next_day_forec.find('div', class_="day") #day part
    night_forec = next_day_forec.find('div', class_='night') #night part

    #scrap day info
    Next_day_temp = day_forec.find('span', class_="large-temp").get_text()
    weather_info['Next_day_temp'] = int(str(Next_day_temp[:-5])) #remove grade sign and 'Макс' word
    RealFeel = str(next_day_forec.find('span', class_='realfeel').string) #RealFeel
    weather_info['Next_day_RF'] = int(RealFeel[10:-1]) #remove word 'RealFeel' from it and grade sign. make it number
    weather_info['Next_day_condition'] = str(next_day_forec.find('div', class_='cond').string) #condition
    weather_info['Next_day_condition'] = re.sub(regex, '', weather_info['Next_day_condition']) #remove spaces
    weather_info['Next_day_condition'] = weather_info['Next_day_condition'][2:-2] #remove \r\n on the sides

    #scrap night info
    Next_night_temp = night_forec.find('span', class_="large-temp").get_text()
    weather_info['Next_night_temp'] = int(str(Next_night_temp[:-4])) #remove grade sign and 'Мін' word
    RealFeel = str(night_forec.find('span', class_='realfeel').string) #RealFeel
    weather_info['Next_night_RF'] = int(RealFeel[10:-1]) #remove word 'RealFeel' from it and grade sign. make it number
    weather_info['Next_night_condition'] = str(night_forec.find('div', class_='cond').string) #condition
    weather_info['Next_night_condition'] = re.sub(regex, '', weather_info['Next_night_condition']) #remove spaces
    weather_info['Next_night_condition'] = weather_info['Next_night_condition'][2:-2] #remove \r\n on the sides

    return weather_info

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
    RealFeel_block = list(RealFeel_block)[6].find_all('td') #take all columns in 6th row
    RealFeel_block = list(RealFeel_block)[1] #select 2nd col
    RF_text = str(list(RealFeel_block.children)[1].get_text()) # and make it string

    weather_info['RealFeel'] = int(RF_text) #make it number

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
    td = list(table)[5].find_all('td') #take row with temperature
    for item in td: # for each item in row...
        t_0 = item.find_all('div', class_='t_0') #find items with temperature
        for i in t_0: # for each item with temp
            t = str(i.find('b').get_text()) #get text from it
            table_data.append(int(t))

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
    regex = r".\d"
    temperatures_as_str = re.findall(regex, forecast) #find all numbers
    weather_info['Next_day_temp_max'] = int(temperatures_as_str[0]) #First is Max in Celsius
    weather_info['Next_day_temp_min'] = int(temperatures_as_str[1]) #Second is Min in Celsius

    regex = ".*.\d\d .C.F, " #all =/-, numbers and C/F signs ended with comma and space
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

def get_current_location_accu(raw_page):
    """ Returns current location of Accuweather
        with corresponding links
        Prints City, Country and Region
    """

    """ REMOVE ??? """
    accu_location = {}

    soup = BeautifulSoup(raw_page, 'html.parser')
    location_ul = soup.find('ul', id="country-breadcrumbs")
    #location_list = location_ul.find_all('li')

    return accu_city, accu_country, accu_region

def get_city_accu(raw_page):
    """ Returns list of cities of a Country
        with corresponding links
        Input: page with list of cities
    """

    cities_list = {}

    soup = BeautifulSoup(raw_page, 'html.parser')

    raw_list = soup.find('ul', class_="articles")
    raw_list = raw_list.find_all('a')
    for item in raw_list:
        cities_list[item.get_text()] = item.attrs['href']

    return cities_list

def get_region_accu(raw_page):
    """ Returns list of regions
        with corresponding links
        Input: page with list of regions
    """

    region_list = {}

    soup = BeautifulSoup(raw_page, 'html.parser')

    raw_list = soup.find('ul', class_="articles")
    raw_list = raw_list.find_all('a')
    for item in raw_list:
        region_list[item.get_text()] = item.attrs['href']

    print(region_list)

    return region_list

def get_country_accu(raw_page):
    """ Returns list of countries
        with corresponding links
        Input: page with list of countries
    """
    countries_list = {}

    soup = BeautifulSoup(raw_page, 'html.parser')

    raw_list = soup.find('ul', class_="articles")
    raw_list = raw_list.find_all('a')
    for item in raw_list:
        countries_list[item.get_text()] = item.attrs['href']

    return countries_list

def get_continent_accu(raw_page):
    """ Returns list of continents
        with corresponding links
        Input: page with list of regions
    """
    continent_list = {}

    soup = BeautifulSoup(raw_page, 'html.parser')

    raw_list = soup.find('ul', class_="articles")
    raw_list = raw_list.find_all('a')
    for item in raw_list:
        continent_list[item.get_text()] = item.attrs['href']

    return continent_list

def set_location_accu():
    """ Helps to choose location
        Saves location to config file """

    URL_regions = weather_providers['ACCU']['URL_regions']

    raw_page = ''
    continents = {}
    countries = {}
    regions = {}
    cities = {}

    raw_page = get_raw_page(URL_regions)
    regions = get_continent_accu(raw_page)

    for item in regions:
        print(item)

    choice = input("Введіть назву континенту:\n")
    print('\n')

    raw_page = get_raw_page(regions[choice])
    countries = get_country_accu(raw_page)

    for item in countries:
        print(item)

    choice = input("Введіть назву країни:\n")

    raw_page = get_raw_page(countries[choice])
    regions = get_region_accu(raw_page)

    for item in regions:
        print(item)

    choice = input("Введіть регіон:\n")

    raw_page = get_raw_page(regions[choice])
    cities = get_city_accu(raw_page)

    for item in cities:
        print(item)

    choice = input("Введіть назву міста:\n")

    weather_providers['ACCU']['URL'] = cities[choice]
    #let change other URLs
    url_string = cities[choice]
    regex = "weather-forecast"

    weather_providers['ACCU']['URL_hourly'] = \
                        re.sub(regex, 'hourly-weather-forecast', url_string) #make it for hourly forecast
    weather_providers['ACCU']['URL_next_day'] = \
                        re.sub(regex, 'daily-weather-forecast', url_string) #make for next day forecast
    weather_providers['ACCU']['URL_next_day'] += "?day=2" #add second day notation to the end

def load_location_accu():
    """ Loads location from file """

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
                output_data[1].append(f"{weather_info[item]:.0f}" + ' ' + headers_dict['Deg'])
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

    args = parser.parse_args()

    if args.accu or args.rp5 or args.sin: args.all = False #switch all to False if any of providers called

    if args.all:
        args.accu = args.rp5 = args.sin = True #make all shown

    if args.noforec:
        args.forec = False #set forecast not to show

    return args

def run_app(*args, provider, forec):
    """
    Runs loading, scraping and printing out weather info depending on given flags
    """
    weather_info = {}
    title = provider['Title']
    URL = provider['URL']
    try:
        URL_hourly = provider['URL_hourly']
    except KeyError:
        URL_hourly = provider['URL']
    try:
        URL_next_day = provider['URL_next_day']
    except KeyError:
        URL_next_day = provider['URL']


    raw_page = get_raw_page(URL) #load a page
    if title == 'Accuweather':

        if args[0].loc:
            set_location_accu()
            URL = provider['URL']

        if args[0].next:
            raw_page = get_raw_page(URL_next_day) #load forecast
            info_next_day = get_accu_next_day(raw_page) #run if forecast called
            weather_info.update(info_next_day) #update with forecast

        if not args[0].next:
            weather_info = get_accu_info(raw_page) #extract data from a page
            if forec:
                raw_page = get_raw_page(URL_hourly) #load forecast
                info_hourly = get_accu_hourly(raw_page) #run if forecast called
                weather_info.update(info_hourly) #update with forecast

    elif title == 'RP5':

        if args[0].next:
            raw_page = get_raw_page(URL_next_day)
            info_next_day = get_rp5_next_day(raw_page)
            weather_info.update(info_next_day) #update with forecast

        if not args[0].next:
            weather_info = get_rp5_info(raw_page) #extract data from a page
            if forec:
                raw_page = get_raw_page(URL_hourly) #load forecast
                info_hourly = get_rp5_hourly(raw_page) #run if forecast called
                weather_info.update(info_hourly) #update with forecast

    elif title == 'Sinoptik':

        if args[0].next:
            raw_page = get_raw_page(URL_next_day)
            info_next_day = get_sinoptik_next_day(raw_page)
            weather_info.update(info_next_day)

        if not args[0].next:
            weather_info = get_sinoptik_info(raw_page) #extract data from a page
            if forec:
                raw_page = get_raw_page(URL_hourly) #load forecast
                info_hourly = get_sinoptik_hourly(raw_page) #run if forecast called
                weather_info.update(info_hourly) #update with forecast

    if args[0].next:
        title = title + ", прогноз на завтра"
    else:
        title = title + ", поточна погода"

    output_data = make_printable(weather_info) #create printable
    print_weather(output_data, title) #print weather info on a screen
    """ save loaded data """
    ACTUAL_WEATHER_INFO[title] = weather_info
    ACTUAL_PRINTABLE_INFO[title] = nice_output(output_data, title)

    pass

def main():
    args = take_args()

    if args.accu:
        run_app(args, provider=weather_providers['ACCU'], forec=args.forec)
    if args.rp5:
        run_app(args, provider=weather_providers['RP5'], forec=args.forec)
    if args.sin:
        run_app(args, provider=weather_providers['Sinoptik'], forec=args.forec)
    if args.csv:
        save_csv(ACTUAL_WEATHER_INFO, args.csv)
    if args.save:
        save_txt(ACTUAL_PRINTABLE_INFO, args.save)

if __name__ == "__main__":
    main()
