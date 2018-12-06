"""
Test project
"""

from urllib.request import urlopen, Request
from html import escape, unescape
from bs4 import BeautifulSoup

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

def get_accu_info(raw_page):
    """ Extracts weather info from ACCUWEATHER loaded page
    """
    weather_info = {}

    soup = BeautifulSoup(raw_page, 'html.parser')

    current_cond_div = soup.find('div', id='feed-tabs', class_='panel-list cityforecast') #find block with curr condition
    weather_info['Temperature'] = str(current_cond_div.find('span', class_='large-temp').string) #temperature and convert it to string type
    weather_info['Temperature'] = weather_info['Temperature'][:-1] #remove grade sign
    weather_info['Condition'] = str(current_cond_div.find('span', class_='cond').string) #condition
    RealFeel = str(current_cond_div.find('span', class_='realfeel').string) #RealFeel
    weather_info['RealFeel'] = RealFeel[10:-1] #remove word 'RealFeel' from it and grade sign

    return weather_info

def get_accu_hourly(raw_page):

    weather_info = {}
    soup = BeautifulSoup(raw_page, 'html.parser')

    hourly_data = soup.find('div', class_='hourly-table overview-hourly') #find hourly forecast table
    hourly_data = hourly_data.select('tbody tr span') #extract only <span> with data

    i=0
    hourly_temperature = []
    while i<8: #move 8 times (8 hours forecast)
        hourly_temperature.append(int(list(hourly_data)[i].string[:1]))
        i += 1
        pass
    weather_info['Max'] = max(hourly_temperature)
    weather_info['Min'] = min(hourly_temperature)
    weather_info['Av'] = sum(hourly_temperature) / len(hourly_temperature)

    return weather_info

def get_rp5_info(raw_page):
    """ Extracts data from RP5 loaded page
    """
    weather_info = {}
    soup = BeautifulSoup(raw_page, 'lxml')

    temperature_block = soup.find('div', id = 'ArchTemp') #part with Temperature
    temperature_text = temperature_block.find('span', class_='t_0').string #Actual temperature
    temperature_text = temperature_text[:len(temperature_text) - 3] #remove space and Celsius sign
    weather_info['Temperature'] = temperature_text

    RealFeel_block = soup.find('div', class_='ArchiveTempFeeling') #Looking for RF
    RF_text = RealFeel_block.find('span', class_='t_0').string #actual RF
    RF_text = RF_text[:len(RF_text) - 3] #remove space and Celsius sign
    weather_info['RealFeel'] = RF_text

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

    return weather_info

def get_sinoptik_info(raw_page, TAGS):
    """ Extracts data from Sinoptik loaded page
    """
    weather_info = {}

    soup = BeautifulSoup(raw_page, 'html.parser')
    curr_temp_cond = soup.find('div', class_='lSide')
    cond = list(curr_temp_cond.find('div', class_='img').children)
    cond = str(cond[1]['alt'])
    weather_info['Condition'] = cond

    curr_temp = str(curr_temp_cond.find('p', class_='today-temp').get_text())
    weather_info['Temperature'] = curr_temp[:-2] #delete Celsius sign

    curr_realfeel = soup.find('div', class_='rSide')
    curr_realfeel = curr_realfeel.find('tr', class_='temperatureSens')
    curr_realfeel = str(curr_realfeel.find('td', class_='p1').get_text())
    weather_info['RealFeel'] = curr_realfeel[:-1] #remove grade sign

    return weather_info

def print_weather(weather_info, title):
    """
    Prints weather on a screen
    """
    def create_table(table_data, title):
        first_column_len = len(max(table_data.keys(), key = lambda item: len(item))) + 2
        second_column_len = len(max(table_data.values(), key = lambda item: len(item))) + 2
        width = first_column_len + second_column_len + 1

        print('+' + '-'*(width) + '+')
        print('|' + title.center(width, ' ') + '|')
        print('+' + '-'*(first_column_len) + '+' + '-'*(second_column_len) + '+')
        for item in table_data:
            print('| ' + item.ljust(first_column_len - 1, ' '), end ="")
            print('| ' + table_data[item].ljust(second_column_len-1, ' ') + '|')
        print('+' + '-'*(first_column_len) + '+' + '-'*(second_column_len) + '+')
        pass

    output_data = {'Температура': f"""{weather_info['Temperature']} {unescape('&deg')}C""",
                    'Відчувається як': f"""{weather_info['RealFeel']} {unescape('&deg')}C""",
                    'На небі': weather_info['Condition']}
    create_table(output_data, title)


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
        weather_info = get_accu_info(raw_page) #extract data from a page
        print_weather(weather_info, title) #print weather info on a screen
    elif provider == 'RP5':
        weather_info = get_rp5_info(raw_page) #extract data from a page
        print_weather(weather_info, title) #print weather info on a screen
    elif provider == 'Sinoptik':
        weather_info = get_sinoptik_info(raw_page, TAGS) #extract data from a page
        print_weather(weather_info, title) #print weather info on a screen
    else:
        pass

main('ACCU')
main('RP5')
main('Sinoptik')
