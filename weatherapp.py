"""
Test project
"""

from urllib.request import urlopen, Request
from html import escape, unescape

def get_raw_page(URL):
    """
    Loads a page from given URL
    """
    HEAD = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:63.0) Gecko/201'}
    INFO_REQUEST = Request(URL, headers = HEAD)
    PAGE = urlopen(INFO_REQUEST).read()
    PAGE = str(PAGE, encoding = 'utf-8')

    return PAGE

def get_data_by_tags(html_page, open_tag, close_tag = None, end_shift = 0):
    """ Returns a string from raw data starting after a tag finded
        Closing tag is optional. end_shift - number of symbols to move left"""

    start = html_page.find(open_tag) + len(open_tag)
    if close_tag:
        end = html_page.find(close_tag, start + 1)
    else:
        end = len(html_page) - 1
    html_string = html_page[start:end - end_shift]

    return html_string

def get_accu_info(raw_page, TAGS):
    """ Extracts weather info from ACCUWEATHER loaded page
    """
    weather_info = {}

    """Condition"""
    weather_info['Condition'] = get_data_by_tags(raw_page, TAGS['Condition_open_tag'],
                                TAGS['Condition_close_tag'], 1)

    """Temperature"""
    temp = int(get_data_by_tags(raw_page, TAGS['TEMP_open_tag'],
                                TAGS['TEMP_close_tag'], 1))
    weather_info['Temperature'] = (temp - 32) * 5 / 9 #convert to celsius

    """RealFeel"""
    weather_info['RealFeel'] = get_data_by_tags(raw_page, TAGS['RealFeel_open_tag'],
                                TAGS['RealFeel_close_tag'], 3)
    return weather_info

def get_rp5_info(raw_page, TAGS):
    """ Extracts data from RP5 loaded page
    """
    return weather_info

def get_sinoptik_info(raw_page, TAGS):
    """ Extracts data from Sinoptik loaded page
    """
    return weather_info

def print_weather(weather_info):
    """
    Prints weather on a screen
    """
    print('\nПоточна погода за даними Accuweather:\n')
    print(f"Температура {weather_info['Temperature']:.0f} {unescape('&deg')}C,"
         f"відчувається як {weather_info['RealFeel']} {unescape('&deg')}C,"
         f" на небі - {weather_info['Condition']}\n")

def main(URL, TAGS):
    raw_page = get_raw_page(URL) #load a page
    weather_info = get_accu_info(raw_page, TAGS) #extract data from a page
    print_weather(weather_info) #print weather info on a screen

weather_providers = {'ACCU': {'Title': 'Accuweather',
                                'URL': "https://www.accuweather.com/uk/ua/kyiv/324505/weather-forecast/324505",
                                'TAGS': {'Condition_open_tag': 'txt : \'', 'Condition_close_tag': ',',
                                        'TEMP_open_tag': 'temp_f : \'', 'TEMP_close_tag': ',',
                                        'RealFeel_open_tag': 'rf : \'', 'RealFeel_close_tag': ','}}}


URL = "https://www.accuweather.com/uk/ua/kyiv/324505/weather-forecast/324505"
TAGS = {'Condition_open_tag': 'txt : \'', 'Condition_close_tag': ',',
        'TEMP_open_tag': 'temp_f : \'', 'TEMP_close_tag': ',',
        'RealFeel_open_tag': 'rf : \'', 'RealFeel_close_tag': ','}

main(weather_providers['ACCU']['URL'], weather_providers['ACCU']['TAGS'])
