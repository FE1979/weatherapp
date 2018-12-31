from urllib.request import urlopen, Request
from urllib.parse import quote, unquote
from urllib import parse
from bs4 import BeautifulSoup
import re
import os
import time
import pathlib
import hashlib

class WeatherProvider:
    """ Class for all weather providers"""
    def __init__(self, Title, URL, URL_locations, Location, Cache_path, Caching_time):
        self.title = Title
        self.url = URL
        self.url_locations = URL_locations
        self.location = Location
        self.cache_path = Cache_path
        self.caching_time = Caching_time

    def get_raw_page(self, URL, force_reload = False):
        """
        Loads a page from given URL
        """

        if not self.valid_cache(URL) or force_reload:

            HEAD = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:63.0) Gecko/201'}
            INFO_REQUEST = Request(URL, headers = HEAD)
            PAGE = urlopen(INFO_REQUEST).read()

            self.save_cache(PAGE, URL)

        else:
            PAGE = self.load_cache(URL)

        PAGE = str(PAGE, encoding = 'utf-8')

        return PAGE

    def get_cache_file_path(self, URL):
        """ Gets cache file full path """

        filename = hashlib.md5(URL.encode('utf-8')).hexdigest() + '.wbc'
        path = pathlib.Path(self.cache_path)
        cache_file_path = path.joinpath(filename)

        return cache_file_path

    def save_cache(self, data, URL):
        """ Saves data to cache file in cache directory
            located in application directory
        """

        cache_file = self.get_cache_file_path(URL)

        if cache_file.parent.exists():
            with open(cache_file, 'wb') as f:
                f.write(data)
        else:
            os.mkdir(cache_file.parent)
            with open(cache_file, 'wb') as f:
                f.write(data)

    def get_cache_time(self, URL):
        """ Gets cache file creating time """

        cache_file = self.get_cache_file_path(URL)

        if cache_file.exists():
            cache_time = cache_file.stat().st_mtime
        else:
            cache_time = 0

        return cache_time

    def load_cache(self, URL):
        """ Loads cache for given URL """

        cache_file = self.get_cache_file_path(URL)

        with open(cache_file, 'rb') as f:
            PAGE = f.read()

        return PAGE

    def valid_cache(self, URL):
        """ Returns True if cache file exists and valid
            False if not
        """

        cache_file = self.get_cache_file_path(URL)

        if cache_file.exists():
            cache_time = cache_file.stat().st_mtime
            if time.time() < self.get_cache_time(URL) + self.caching_time * 60:
                cache_valid = True
            else:
                cache_valid = False

        else:
            cache_valid = False

        return cache_valid

    def clear_cache(self):
        """ Removes cache directory """

        path = pathlib.Path(self.Cache_path)

        answer = input('Do you really want to remove all cache files with directory? Y/N\n')
        if answer.lower() == 'y':
            for item in list(path.glob('*.*')):
                item.unlink()
            print('Files removed')
            path.rmdir()
            print('Directory removed')
        else:
            pass

class AccuProvider(WeatherProvider):
    """ Special class for Accuweather"""

    def __init__(self, Title, URL, URL_locations, Location, Cache_path, \
                                    Caching_time, URL_hourly, URL_next_day):
        super(AccuProvider, self).__init__(Title, URL, URL_locations,\
                                        Location, Cache_path, Caching_time)
        self.url_hourly = URL_hourly
        self.url_next_day = URL_next_day

    """ ACCU methods """
    def get_info(self):
        """ Extracts weather info from ACCUWEATHER loaded page using BS4
            returns info in dictionary: Temperature, Condition, RealFeel
        """
        weather_info = {}

        soup = BeautifulSoup(self.raw_page, 'html.parser')

        current_cond_div = soup.find('div', id='feed-tabs', class_='panel-list cityforecast') #find block with curr condition
        weather_info['Temperature'] = str(current_cond_div.find('span', class_='large-temp').string) #temperature and convert it to string type
        weather_info['Temperature'] = int(weather_info['Temperature'][:-1]) #remove grade sign, make it number
        weather_info['Condition'] = str(current_cond_div.find('span', class_='cond').string) #condition
        RealFeel = str(current_cond_div.find('span', class_='realfeel').string) #RealFeel
        weather_info['RealFeel'] = int(RealFeel[10:-1]) #remove word 'RealFeel' from it and grade sign. make it number

        return weather_info

    def get_hourly(self):
        """ Gets temperature forecast for next 8 hours
            Returns dict: Max, Min, Average, Forecast horizon in number of hours
        """

        weather_info = {}
        soup = BeautifulSoup(self.raw_page, 'html.parser')

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

    def get_next_day(self):
        """ Extracts weather info for next day
            returns info in dictionary: Temperature, Condition, RealFeel
        """
        weather_info = {}
        regex = "  1?" #to remove unnessecary symbols

        soup = BeautifulSoup(self.raw_page, 'html.parser')

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

    def get_current_location(self):

        """ Returns current location of Accuweather
            with corresponding links
            Prints City, Region, Country and Continent
        """

        accu_location = []

        soup = BeautifulSoup(self.raw_page, 'html.parser')
        location_ul = soup.find('ul', id="country-breadcrumbs")
        location = location_ul.find_all('a')

        for item in location:
            if item.attrs['href'] is not None:
                accu_location.append(item.get_text())

        return accu_location

    def browse_location(self, level = 0, URL_location = None):
        """ Browse recursively locations of ACCU
            Starts from continents
            defaults: level = 0: continent level
                      URL_location: page with continents
            Each next call with new URL and level + 1
            Returns collection of URLs: URL (current weather), URL_hourly and URL_next_day
        """
        if URL_location is None:
            URL_location = self.url_locations

        levels = ['continent', 'country', 'region', 'city'] #for user input and level check
        raw_page = self.get_raw_page(URL_location) #read locations
        locations_list = {} #locations associated with their urls
        location_set = {} #result of func

        soup = BeautifulSoup(raw_page, 'html.parser') #parse page
        raw_list = soup.find('ul', class_="articles") #find list of locations
        raw_list = raw_list.find_all('a') #take all links in list of locations

        for item in raw_list: #associate location with ulr
            locations_list[item.get_text()] = item.attrs['href']

        for item in locations_list: #print out locations
            print(item)

        choice = input(f"\nEnter {levels[level]} name:\n") #user input

        #call this function again with new locations
        if level <3:

            location_set = self.browse_location(level+1, URL_location = locations_list[choice])

        if level == 3:
            location_set['URL'] = locations_list[choice]
            #let change other URLs
            url_string = locations_list[choice]
            regex = "weather-forecast"

            location_set['URL_hourly'] = \
                                re.sub(regex, 'hourly-weather-forecast', url_string) #make it for hourly forecast
            location_set['URL_next_day'] = \
                                re.sub(regex, 'daily-weather-forecast', url_string) #make for next day forecast
            location_set['URL_next_day'] += "?day=2" #add second day notation to the end
            location_set['Location'] = choice

        return location_set

    def set_location(self, location_set):
        """ Sets to the config ACCU location """

        self.url = location_set['URL']
        self.url_hourly = location_set['URL_hourly']
        self.url_next_day = location_set['URL_next_day']
        self.location = location_set['Location']

class RP5_Provider(WeatherProvider):

    def __init__(self, Title, URL, URL_locations, Location, Cache_path, \
                                    Caching_time):
        super(RP5_Provider, self).__init__(Title, URL, URL_locations,\
                                        Location, Cache_path, Caching_time)
        pass

    def get_info(self):
        """ Extracts data from RP5 loaded page
            returns info in dictionary: Temperature, Condition, RealFeel
        """
        weather_info = {}
        soup = BeautifulSoup(self.raw_page, 'lxml')

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

    def get_hourly(self):
        """ Gets temperature forecast for next 8 hours
            Returns dict: Max, Min, Average, Forecast horizon in number of hours
        """

        weather_info = {}
        table_data = []
        soup = BeautifulSoup(self.raw_page, 'lxml')

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

    def get_next_day(self):
        """ Extracts weather info for next day
            returns info in dictionary: Temperature, Condition, RealFeel
            using RegEx
        """
        weather_info = {}

        soup = BeautifulSoup(self.raw_page, 'lxml')

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

    def browse_location(self, level = 0, URL_location = None ):
        """ Browse recursively locations of RP5
            Starts from all countries
            defaults: level = 0: country level
                      URL_location: page with countries
            Each next call with new URL and level + 1
            Returns: URL (current weather), name of Location
        """
        if URL_location == None:
            URL_location = self.url_locations

        levels = ['country', 'region', 'city'] #for user input and level check
        location_set = {}
        locations_list = {} #locations associated with their urls
        raw_page = self.get_raw_page(URL_location) #read locations

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
            location_set = self.browse_location(level+1, locations_list[choice])

        if level == 2: #final if city level
            location_set['URL'] = locations_list[choice]
            location_set['Location'] = choice

        return location_set

    def set_location(self, location_set):
        """ Sets RP5 location to the config """

        self.url = location_set['URL']
        self.location = location_set['Location']

    def search_location():
        """ Searches location typed by user through RP5 """

        location_search = input("Type location to search\n")
        data = location_search.encode('utf-8')

        URL_search = weather_providers['RP5']['URL_search']
        HEAD_search = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:63.0) Gecko/201'}
        SEARCH_REQUEST = Request(URL_search, data = data, headers = HEAD_search)
        PAGE_SEARCH = urlopen(SEARCH_REQUEST).read()
        PAGE_SEARCH = str(PAGE_SEARCH, encoding = 'utf-8')

        print(PAGE_SEARCH)
