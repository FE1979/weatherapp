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
    weather_info['Temperature'] = str(int((temp - 32) * 5 / 9)) #convert to celsius
    #weather_info['Temperature'] = {.0}.format(weather_info['Temperature'])

    """RealFeel"""
    weather_info['RealFeel'] = get_data_by_tags(raw_page, TAGS['RealFeel_open_tag'],
                                TAGS['RealFeel_close_tag'], 3)
    return weather_info

def get_rp5_info(raw_page, TAGS):
    """ Extracts data from RP5 loaded page
    """
    weather_info = {}

    """Temperature"""
    weather_info['Temperature'] = get_data_by_tags(raw_page, TAGS['TEMP_open_tag'], TAGS['TEMP_close_tag'], 7)

    """Condition"""
    weather_info['Condition'] = get_data_by_tags(raw_page, TAGS['Condition_1'])
    weather_info['Condition'] = get_data_by_tags(weather_info['Condition'], TAGS['Condition_row'])
    weather_info['Condition'] = get_data_by_tags(weather_info['Condition'], TAGS['Condition_row'])
    weather_info['Condition'] = get_data_by_tags(weather_info['Condition'], TAGS['Condition_2'], TAGS['Condition_close_tag'], )

    """RealFeel"""
    weather_info['RealFeel'] = get_data_by_tags(raw_page, TAGS['RealFeel_1'])
    weather_info['RealFeel'] = get_data_by_tags(weather_info['RealFeel'], TAGS['RealFeel_2'], TAGS['RealFeel_close_tag'])

    return weather_info

def get_sinoptik_info(raw_page, TAGS):
    """ Extracts data from Sinoptik loaded page
    """
    weather_info = {}
    raw_page = get_data_by_tags(raw_page, TAGS['SINOPTIK_open_tag'], TAGS['SINOPTIK_close_tag'])

    """Temperature"""
    weather_info['Temperature'] = get_data_by_tags(raw_page, TAGS['TEMP_open_tag'], TAGS['TEMP_close_tag'], 6)

    """Condition"""
    weather_info['Condition'] = get_data_by_tags(raw_page, TAGS['Condition_1'])
    weather_info['Condition'] = get_data_by_tags(weather_info['Condition'], TAGS['Condition_2'], TAGS['Condition_close_tag'])

    """RealFeel"""
    weather_info['RealFeel'] = get_data_by_tags(raw_page, TAGS['RealFeel_open_tag_1'])
    weather_info['RealFeel'] = get_data_by_tags(weather_info['RealFeel'], TAGS['RealFeel_open_tag_2'], TAGS['RealFeel_close_tag'], 5)

    return weather_info

def print_weather(weather_info, title):
    """
    Prints weather on a screen
    """
    print(f"\nПоточна погода за даними {title}:\n")
    print(f"Температура {weather_info['Temperature']} {unescape('&deg')}C,"
         f" відчувається як {weather_info['RealFeel']} {unescape('&deg')}C,"
         f" на небі - {weather_info['Condition']}\n")

def main(provider):
    weather_providers = {
    'ACCU': {'Title': 'Accuweather',
            'URL': "https://www.accuweather.com/uk/ua/kyiv/324505/weather-forecast/324505",
            'TAGS': {'Condition_open_tag': 'txt : \'',
                    'Condition_close_tag': ',',
                    'TEMP_open_tag': 'temp_f : \'',
                    'TEMP_close_tag': ',',
                    'RealFeel_open_tag': 'rf : \'',
                    'RealFeel_close_tag': ','}},
    'RP5': {'Title': 'RP5',
            'URL': "http://rp5.ua/%D0%9F%D0%BE%D0%B3%D0%BE%D0%B4%D0%B0_%D0%B2_%D0%9A%D0%B8%D1%94%D0%B2%D1%96",
            'TAGS': {'Condition_1': "ftab_1_content",
                    'Condition_2': "tooltip(this, \'<b>",
                    'Condition_row': '</tr',
                    'Condition_close_tag': "</b>",
                    'TEMP_open_tag': '\"t_0\" style=\"display: block;\">',
                    'TEMP_close_tag': "<",
                    'RealFeel_1': "f_temperature",
                    'RealFeel_2': "<div class=\"t_0\">",
                    'RealFeel_close_tag': "</b>"}},
    'Sinoptik': {'Title': 'Sinoptik',
            'URL': "https://ua.sinoptik.ua/%D0%BF%D0%BE%D0%B3%D0%BE%D0%B4%D0%B0-%D0%BA%D0%B8%D1%97%D0%B2",
            'TAGS': {'SINOPTIK_open_tag': "<div class=\"wMain clearfix\">",
                    'SINOPTIK_close_tag': "<div class=\"wDescription clearfix\">",
                    'Condition_1': "today-time",
                    'Condition_2': "alt=\"",
                    'Condition_close_tag': "\"",
                    'TEMP_open_tag': "today-temp\">",
                    'TEMP_close_tag': "<",
                    'RealFeel_open_tag_1': "<tr class=\"temperatureSens\">",
                    'RealFeel_open_tag_2': "cur\" >",
                    'RealFeel_close_tag': "<"}}
    }

    title = weather_providers[provider]['Title']
    URL = ''
    URL = weather_providers[provider]['URL']
    TAGS = weather_providers[provider]['TAGS']

    raw_page = get_raw_page(URL) #load a page

    if provider == 'ACCU':
        weather_info = get_accu_info(raw_page, TAGS) #extract data from a page
        print_weather(weather_info, title) #print weather info on a screen
    elif provider == 'RP5':
        weather_info = get_rp5_info(raw_page, TAGS) #extract data from a page
        print_weather(weather_info, title) #print weather info on a screen
    elif provider == 'Sinoptik':
        weather_info = get_sinoptik_info(raw_page, TAGS) #extract data from a page
        print_weather(weather_info, title) #print weather info on a screen
    else:
        pass

main('ACCU')
main('RP5')
main('Sinoptik')
