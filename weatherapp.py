"""
Test project
"""

from urllib.request import urlopen, Request
from html import escape, unescape
from bs4 import BeautifulSoup
import sys
import argparse

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

    RealFeel_block = soup.find('div', class_='ArchiveTempFeeling') #Looking for RF
    RF_text = RealFeel_block.find('span', class_='t_0').string #actual RF
    RF_text = RF_text[:len(RF_text) - 3] #remove space and Celsius sign
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
    td = list(table)[4].find_all('td') #take row with temperature
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

def print_weather(output_data, title):
    """
    Prints weather on a screen
    input data - list of two lists: headers and values
    """
    def create_table(table_data, title):
        first_column_len = len(max(table_data[0], key = lambda item: len(item))) + 2
        second_column_len = len(max(table_data[1], key = lambda item: len(item))) + 2
        width = first_column_len + second_column_len + 1
        counter = len(table_data[0])
        i = 0

        #print top of table with title
        print('+' + '-'*(width) + '+')
        print('|' + title.center(width, ' ') + '|')
        print('+' + '-'*(first_column_len) + '+' + '-'*(second_column_len) + '+')

        while i < counter: #print out headers and values
            print('| ' + table_data[0][i].ljust(first_column_len - 1, ' '), end ="")
            print('| ' + table_data[1][i].ljust(second_column_len-1, ' ') + '|')
            i += 1
            pass
        #bottom line
        print('+' + '-'*(first_column_len) + '+' + '-'*(second_column_len) + '+')
        pass

    create_table(output_data, title)

def make_printable(weather_info):
    """ Transform weather data to printable format
        headers_dict - translation dictionary
        temperature_heads - to insert Celsius sign if needed
        print_order - to define which way weather_info will show
    """
    headers_dict = {'Temperature': 'Температура', 'RealFeel': 'Відчувається як',
                    'Condition': 'На небі', 'Max': 'Максимальна', 'Min': 'Мінімальна',
                    'Av': 'Середня', 'Num': 'Прогноз на, годин', 'Deg': f"{unescape('&deg')}C"}
    temperature_heads = ['Temperature', 'RealFeel', 'Max', 'Min', 'Av']
    print_order = ['Temperature', 'RealFeel', 'Condition', 'Num', 'Max', 'Min', 'Av']
    output_data = [[],[]]

    for item in print_order:
        if item in weather_info.keys():
            if item in temperature_heads: #if we need to show Celsius
                output_data[0].append(headers_dict[item])
                output_data[1].append(f"{weather_info[item]:.0f}" + ' ' + headers_dict['Deg'])
            else:
                output_data[0].append(headers_dict[item])
                output_data[1].append(str(weather_info[item]))
        else:
            pass

    return output_data

def main(provider):
    weather_providers = {
    'ACCU': {'Title': 'Accuweather',
            'URL': "https://www.accuweather.com/uk/ua/kyiv/324505/weather-forecast/324505",
            'URL_hourly': "https://www.accuweather.com/uk/ua/kyiv/324505/hourly-weather-forecast/324505",
            },
    'RP5': {'Title': 'RP5',
            'URL': "http://rp5.ua/%D0%9F%D0%BE%D0%B3%D0%BE%D0%B4%D0%B0_%D0%B2_%D0%9A%D0%B8%D1%94%D0%B2%D1%96",
            },
    'Sinoptik': {'Title': 'Sinoptik',
            'URL': "https://ua.sinoptik.ua/%D0%BF%D0%BE%D0%B3%D0%BE%D0%B4%D0%B0-%D0%BA%D0%B8%D1%97%D0%B2",
            }
    }

    title = weather_providers[provider]['Title']
    URL = ''
    URL = weather_providers[provider]['URL']

    raw_page = get_raw_page(URL) #load a page

    if provider == 'ACCU':
        weather_info = get_accu_info(raw_page) #extract data from a page
        raw_page = get_raw_page(weather_providers[provider]['URL_hourly']) #load forecast
        ACCU_hourly = get_accu_hourly(raw_page)
        weather_info.update(ACCU_hourly) #update with forecast

        output_data = make_printable(weather_info) #create printable
        print_weather(output_data, title) #print weather info on a screen

    elif provider == 'RP5':
        weather_info = get_rp5_info(raw_page) #extract data from a page

        RP5_hourly = get_rp5_hourly(raw_page)
        weather_info.update(RP5_hourly)

        output_data = make_printable(weather_info)
        print_weather(output_data, title)

    elif provider == 'Sinoptik':
        weather_info = get_sinoptik_info(raw_page) #extract data from a page

        Sinoptik_hourly = get_sinoptik_hourly(raw_page)
        weather_info.update(Sinoptik_hourly)

        output_data = make_printable(weather_info)
        print_weather(output_data, title)
    else:
        pass

if __name__ == "__main__":
    main('ACCU')
    main('RP5')
    main('Sinoptik')
