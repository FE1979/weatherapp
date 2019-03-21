""" Providers
    AccuProvider - accuweather.com
    RP5_Provider - rp5.ua
    SinoptikProvider - sinoptik.ua
"""

from urllib.request import urlopen, Request
from urllib.parse import quote, unquote
from urllib import parse
from bs4 import BeautifulSoup
import sys
import re
import os
import time
import pathlib
import hashlib

from abstract.abstract import WeatherProvider
import config.decorators


class AccuProvider(WeatherProvider):
    """ Class for Accuweather"""

    title = "Accuweather"

    def get_info(self):
        """ Extracts weather info from ACCUWEATHER loaded page using BS4
            Returns info in dictionary:
            weather_info = {
                'Temperature': # temperature
                'Condition':   # weather condition
                'RealFeel':    # real feel temperature
                }
        """

        weather_info = {}

        soup = BeautifulSoup(self.raw_page, 'html.parser')

        # find block with current condition
        current_cond_div = \
            soup.find('div', id='feed-tabs', class_='panel-list cityforecast')
        # get temperature and convert it to string type
        weather_info['Temperature'] = \
            str(current_cond_div.find('span', class_='large-temp').string)
        # remove grade sign, make it number
        weather_info['Temperature'] = int(weather_info['Temperature'][:-1])
        # get weather condition
        weather_info['Condition'] = \
            str(current_cond_div.find('span', class_='cond').string)
        # get real feel temperature
        RealFeel = str(current_cond_div.find('span', class_='realfeel').string)
        # remove word 'RealFeel' from it and grade sign. make it number
        weather_info['RealFeel'] = int(RealFeel[10:-1])

        return weather_info

    def get_hourly(self):
        """ Gets temperature forecast for next 8 hours
            Returns info in dictionary:
            weather_info = {
                'Max': # maximum temperature forecast
                'Min': # minimum temperature forecast
                'Av':  # average temperature forecast
                'Num': # forecast horizon in hours
                }
        """

        weather_info = {}
        soup = BeautifulSoup(self.raw_page, 'html.parser')

        # find hourly forecast table
        hourly_data = soup.find('div', class_='hourly-table overview-hourly')
        # extract only <span> with data
        hourly_data = hourly_data.select('tbody tr span')

        # run 8 times through data (8 hours forecast)
        i = 0
        hourly_temperature = []
        while i < 8:
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
            Returns info in dictionary:
            weather_info = {
                'Max': # maximum temperature forecast
                'Min': # minimum temperature forecast
                'Av':  # average temperature forecast
                'Num': # forecast horizon in hours
                }
        """

        weather_info = {}
        regex = "  1?"  # to remove unnessecary symbols

        soup = BeautifulSoup(self.raw_page, 'html.parser')
        # find day/night forecast panel
        next_day_forec = soup.find('div', id="detail-day-night")

        day_forec = next_day_forec.find('div', class_="day")  # day part
        night_forec = next_day_forec.find('div', class_='night')  # night part

        # scrap day info
        Next_day_temp = day_forec.find('span', class_="large-temp").get_text()
        # remove grade sign and 'Макс' word
        weather_info['Next_day_temp'] = int(str(Next_day_temp[:-5]))
        # RealFeel
        RealFeel = str(next_day_forec.find('span', class_='realfeel').string)
        # remove word 'RealFeel' from it and grade sign. make it number
        weather_info['Next_day_RF'] = int(RealFeel[10:-1])
        # condition
        weather_info['Next_day_condition'] = \
            str(next_day_forec.find('div', class_='cond').string)
        # remove spaces
        weather_info['Next_day_condition'] = \
            re.sub(regex, '', weather_info['Next_day_condition'])
        # remove \r\n on the sides
        weather_info['Next_day_condition'] = \
            weather_info['Next_day_condition'][2:-2]

        # scrap night info
        Next_night_temp = \
            night_forec.find('span', class_="large-temp").get_text()
        # remove grade sign and 'Мін' word
        weather_info['Next_night_temp'] = int(str(Next_night_temp[:-4]))
        # RealFeel
        RealFeel = str(night_forec.find('span', class_='realfeel').string)
        # remove word 'RealFeel' from it and grade sign. make it number
        weather_info['Next_night_RF'] = int(RealFeel[10:-1])
        # condition
        weather_info['Next_night_condition'] = \
            str(night_forec.find('div', class_='cond').string)
        # remove spaces
        weather_info['Next_night_condition'] = \
            re.sub(regex, '', weather_info['Next_night_condition'])
        # remove \r\n on the sides
        weather_info['Next_night_condition'] = \
            weather_info['Next_night_condition'][2:-2]

        return weather_info

    def get_current_location(self):
        """ Returns current location of Accuweather
            with corresponding links
            :return: City, Region, Country and Continent
            :rtype: list
        """

        accu_location = []

        soup = BeautifulSoup(self.raw_page, 'html.parser')
        location_ul = soup.find('ul', id="country-breadcrumbs")
        location = location_ul.find_all('a')

        for item in location:
            if item.attrs['href'] is not None:
                accu_location.append(item.get_text())

        return accu_location

    def browse_location(self, level=0, URL_location=None):
        """ Browse recursively locations of ACCU
            Starts from continents
            Defaults: level = 0: continent level
                      URL_location: page with continents
            Each next call with new URL and level + 1
            :return: URL, URL_hourly, URL_next_day and Location
            :rtype: list
        """

        if URL_location is None:
            URL_location = self.URL_locations

        # container for user input and level check
        levels = ['continent', 'country', 'region', 'city']
        raw_page = self.get_raw_page(URL_location)  # read locations
        locations_list = {}  # locations associated with their urls
        location_set = {}  # return

        soup = BeautifulSoup(raw_page, 'html.parser')  # parse page
        raw_list = soup.find('ul', class_="articles")  # find list of locations
        raw_list = raw_list.find_all('a')  # get all links in list of locations

        for item in raw_list:  # associate location with ulr
            locations_list[item.get_text()] = item.attrs['href']

        for item in locations_list:  # print out locations
            self.app.stdout.write(f"{item}\n")

        choice = input(f"\nEnter {levels[level]} name:\n")  # user input

        # call this function again with new locations
        if level < 3:
            try:
                location_set = self.browse_location(
                    level+1, URL_location=locations_list[choice])
            except KeyError:
                self.logger.error(
                    'Wrong name entered. ' +
                    'Please, restart application and try again')
                sys.exit()

        # end of browsing
        if level == 3:
            location_set['URL'] = locations_list[choice]
            url_string = locations_list[choice]
            regex = "weather-forecast"

            location_set['URL_hourly'] = \
                re.sub(regex, 'hourly-weather-forecast', url_string)
            location_set['URL_next_day'] = \
                re.sub(regex, 'daily-weather-forecast', url_string)
            location_set['URL_next_day'] += "?day=2"
            location_set['Location'] = choice

        return location_set

    def set_location(self, location_set):
        """ Sets to the config ACCU location
            :param location_set: URLs and location from browse_location
        """

        self.URL = location_set['URL']
        self.URL_hourly = location_set['URL_hourly']
        self.URL_next_day = location_set['URL_next_day']
        self.Location = location_set['Location']


class RP5_Provider(WeatherProvider):
    """ Class for RP5 """

    title = "RP5"

    def get_info(self):
        """ Extracts data from RP5 loaded page
            Returns info in dictionary:
            weather_info = {
                'Temperature': # temperature
                'Condition':   # weather condition
                'RealFeel':    # real feel temperature
                }
        """

        weather_info = {}
        soup = BeautifulSoup(self.raw_page, 'lxml')

        # get part with Temperature
        temperature_block = soup.find('div', id='ArchTemp')
        # get actual temperature
        temperature_text = temperature_block.find('span', class_='t_0').string
        # remove space and Celsius sign
        temperature_text = temperature_text[:len(temperature_text) - 3]
        # make it integer
        weather_info['Temperature'] = int(temperature_text)

        # take table with short hourly description
        RealFeel_block = soup.find('table', id='forecastTable_1')
        # take all rows
        RealFeel_block = RealFeel_block.find_all('tr')
        # find row index with RealFeel
        for item in RealFeel_block:
            id = item.find('a', id="f_temperature")
            if id is None:
                pass
            else:
                index_RF = RealFeel_block.index(item)
        # take all columns in row
        RealFeel_block = list(RealFeel_block)[index_RF].find_all('td')
        # select 2nd column
        RealFeel_block = list(RealFeel_block)[1]
        # and make it string
        try:
            RF_text = str(list(RealFeel_block.children)[1].get_text())
        except IndexError:
            RF_text = ''  # if no data keep it blank

        try:
            weather_info['RealFeel'] = int(RF_text)  # make it integer
        except ValueError:
            weather_info['RealFeel'] = ''  # if it is blank do keep it

        # take table with short hourly description
        Cond_block = soup.find('table', id='forecastTable_1')
        # take all rows
        Cond_block = Cond_block.find_all('tr')
        # take all columns in 3rd row
        Cond_block = list(Cond_block)[2].find_all('td')
        # select 2nd column
        Cond_block = list(Cond_block)[1]
        # and make it string
        Cond_text = str(list(Cond_block.children)[1])

        start_tag = 'b&gt;'
        end_tag = '&lt'
        start = Cond_text.find(start_tag) + len(start_tag)
        end = Cond_text.find(end_tag, start)
        weather_info['Condition'] = Cond_text[start:end]

        return weather_info

    def get_hourly(self):
        """ Gets temperature forecast for next 8 hours
            Returns info in dictionary:
            weather_info = {
                'Max': # maximum temperature forecast
                'Min': # minimum temperature forecast
                'Av':  # average temperature forecast
                'Num': # forecast horizon in hours
                }
        """

        weather_info = {}
        table_data = []
        soup = BeautifulSoup(self.raw_page, 'lxml')

        # get table
        table = soup.find('table', id='forecastTable_1')
        # take all rows
        table = table.find_all('tr')
        # find row index with Temperature
        for item in table:
            id = item.find('a', id="t_temperature")
            if id is None:
                pass
            else:
                index_T = table.index(item)
        # take row with temperature
        td = list(table)[index_T].find_all('td')
        for item in td:
            # find div with temperature
            t_0 = item.find('div', class_='t_0')
            # if there is one
            if t_0 is not None:
                t = str(t_0.get_text())  # get text from it
                table_data.append(int(t))  # and append to data

        weather_info['Max'] = max(table_data)
        weather_info['Min'] = min(table_data)
        weather_info['Av'] = sum(table_data) / len(table_data)
        weather_info['Num'] = len(table_data)

        return weather_info

    def get_next_day(self):
        """ Extracts weather info for next day using RegEx
            weather_info = {
                'Next_day_temp_max':  # maximum temperature
                'Next_day_temp_min':  # minimum temperature 
                'Next_day_condition': # weather condition for next day
                }
        """
        weather_info = {}

        soup = BeautifulSoup(self.raw_page, 'lxml')

        # get string with short forecast
        forecast = soup.find('div', id="forecastShort-content").get_text()
        # Extract forecast: Max, Min temperature and condition
        regex = "Завтра.*\. "
        # find starting point of forecast info
        forecast_start = re.search(regex, forecast)
        forecast = forecast[forecast_start.start():forecast_start.end()]
        regex = r".\d?\d"
        # find all numbers
        temperatures_as_str = re.findall(regex, forecast)
        weather_info['Next_day_temp_max'] = int(temperatures_as_str[0])
        weather_info['Next_day_temp_min'] = int(temperatures_as_str[1])

        # all +/-, numbers and C/F signs ended with comma and space
        regex = ".*.\d\d .C.F ?, "
        # find starting point of condition description
        cond_pos = re.search(regex, forecast)
        # get a condition string with Capital first letter
        forecast = forecast[cond_pos.end():].capitalize()
        regex = "  +"
        weather_info['Next_day_condition'] = re.sub(regex, '', forecast)

        return weather_info

    def browse_location(self, level=0, URL_location=None):
        """ Browse recursively locations of ACCU
            Starts from country
            Defaults: level = 0: country level
                      URL_location: page with location links
            Each next call with new URL and level + 1
            :return: URL, URL_hourly, URL_next_day and Location
            :rtype: list
        """

        if URL_location is None:
            URL_location = self.URL_locations
        # container for user input and level check
        levels = ['country', 'region', 'city']
        location_set = {}
        locations_list = {}  # locations associated with their urls
        raw_page = self.get_raw_page(URL_location)  # read locations

        soup = BeautifulSoup(raw_page, 'lxml')  # parse page
        table = soup.find('div', class_="countryMap")  # find table

        # get all links on country level
        if level == 0:
            links = table.find_all('div', class_="country_map_links")

            # get URLs, decode and save to the table
            for item in links:
                link = item.find('a')
                url_decoded = quote(link.attrs['href'])
                locations_list[link.get_text()] = "http://rp5.ua" + url_decoded

            for item in locations_list:
                self.app.stdout.write(f"{item}\n")

        # do it for next level
        if level == 1:
            links = table.find_all('a', class_='href12')

            for item in links:
                url_decoded = quote(item.attrs['href'])
                locations_list[item.attrs['title']] = \
                    "http://rp5.ua/" + url_decoded

            for item in locations_list:
                self.app.stdout.write(f"{item}\n")

        # do it for next level
        if level == 2:
            links = table.find_all('a')

            for item in links:
                url_decoded = quote(item.attrs['href'])
                locations_list[item.get_text()] = \
                    "http://rp5.ua/" + url_decoded

            for item in locations_list:
                self.app.stdout.write(f"{item}\n")

        choice = input(f"\nEnter {levels[level]} name:\n")

        # if not city level repeat recursively
        if level < 2:
            try:
                location_set = \
                    self.browse_location(level+1, locations_list[choice])
            except KeyError:
                self.logger.error(
                    'Wrong name entered. ' +
                    'Please, restart application and try again')
                sys.exit()

        # finish on city level
        if level == 2:
            location_set['URL'] = locations_list[choice]
            location_set['Location'] = choice

        return location_set

    def set_location(self, location_set):
        """ Sets RP5 location to the config
            :param set_location: URLs and location given by browse_location
        """

        self.URL = location_set['URL']
        self.Location = location_set['Location']

    def search_location():
        """ Searches location typed by user through RP5 """

        location_search = input("Type location to search\n")
        data = location_search.encode('utf-8')

        URL_search = weather_providers['RP5']['URL_search']
        HEAD_search = {
            'User-Agent':
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:63.0) Gecko/201'
            }
        SEARCH_REQUEST = Request(URL_search, data=data, headers=HEAD_search)
        PAGE_SEARCH = urlopen(SEARCH_REQUEST).read()
        PAGE_SEARCH = str(PAGE_SEARCH, encoding='utf-8')

        self.app.stdout.write(f"{PAGE_SEARCH}\n")


class SinoptikProvider(WeatherProvider):
    """ Class for Sinoptik """

    title = "Sinoptik"

    def get_info(self):
        """ Extracts data from Sinoptik loaded page
            Returns info in dictionary:
            weather_info = {
                'Temperature': # temperature
                'Condition':   # weather condition
                'RealFeel':    # real feel temperature
                }
        """
        weather_info = {}

        soup = BeautifulSoup(self.raw_page, 'html.parser')
        curr_temp_cond = soup.find('div', class_='lSide')
        cond = list(curr_temp_cond.find('div', class_='img').children)
        cond = str(cond[1]['alt'])
        weather_info['Condition'] = cond

        curr_temp = \
            str(curr_temp_cond.find('p', class_='today-temp').get_text())
        # remove Celsius sign and make it integer
        weather_info['Temperature'] = int(curr_temp[:-2])

        curr_realfeel = soup.find('div', class_='rSide')
        curr_realfeel = curr_realfeel.find('tr', class_='temperatureSens')
        curr_realfeel = str(curr_realfeel.find('td', class_='p1').get_text())
        # remove grade sign and make integer
        weather_info['RealFeel'] = int(curr_realfeel[:-1])

        return weather_info

    def get_hourly(self):
        """ Gets temperature forecast for next 8 hours
            Returns info in dictionary:
            weather_info = {
                'Max': # maximum temperature forecast
                'Min': # minimum temperature forecast
                'Av':  # average temperature forecast
                'Num': # forecast horizon in hours
                }
        """

        weather_info = {}
        table_data = []

        soup = BeautifulSoup(self.raw_page, 'html.parser')
        table = soup.find('table', class_='weatherDetails')
        table = table.find('tr', class_='temperature')
        table = table.find_all('td')

        for item in list(table):
            t = item.get_text()
            table_data.append(int(t[:-1]))  # remove grade sign

        weather_info['Max'] = max(table_data)
        weather_info['Min'] = min(table_data)
        weather_info['Av'] = sum(table_data) / len(table_data)
        weather_info['Num'] = len(table_data)

        return weather_info

    def get_next_day(self):
        """ Extracts weather info for next day
            Returns info in dictionary:
            weather_info = {
                'Temperature': # temperature
                'Condition':   # weather condition
                'RealFeel':    # real feel temperature
                }
        """
        weather_info = {}

        soup = BeautifulSoup(self.raw_page, 'html.parser')
        next_day_block = soup.find('div', id="bd2")
        regex = "weatherIco.*"  # different weather icons for condition
        next_day_cond = next_day_block.find('div', class_=re.compile(regex))
        weather_info['Next_day_condition'] = str(next_day_cond.attrs['title'])
        # find max temperature
        Next_day_temp = next_day_block.find('div', class_="max")
        Next_day_temp = Next_day_temp.find('span').string
        weather_info['Next_day_temp_max'] = int(Next_day_temp[:-1])
        # find min temp
        Next_day_temp = next_day_block.find('div', class_="min")
        Next_day_temp = Next_day_temp.find('span').string
        weather_info['Next_day_temp_min'] = int(Next_day_temp[:-1])

        return weather_info

    def browse_location(self, level=0, URL_location=None):
        """ Browse recursively locations of Sinoptik
            Starts from continents
            defaults: level = 0: continent level
                      URL_location: page with continents, Europe by default
            Each next call with new URL and level + 1
            :return: URL, URL_hourly, URL_next_day and Location
            :rtype: list
        """
        if URL_location is None:
            URL_location = self.URL_locations

        # container for user input and level check
        levels = ['continent', 'country', 'region', 'city']
        raw_page = self.get_raw_page(URL_location)  # read locations
        locations_list = {}  # locations associated with their urls
        location_set = {}  # return

        """ Continents and countries are on same page
            so if we are on 0 level we should print continents """
        if level == 0:
            soup = BeautifulSoup(raw_page, 'html.parser')  # parse page
            # find list of locations
            raw_list = soup.find('div', class_="mapRightCol")
            # get first div
            raw_list = raw_list.find('div')
            # get all links in list of locations
            raw_list = raw_list.find_all('a')

            for item in raw_list:  # associate location with ulr
                url_decoded = quote(item.attrs['href'])
                locations_list[item.get_text()] = "https:" + url_decoded

            for item in locations_list:  # print out locations
                self.app.stdout.write(f"{item}\n")

        # if country or region level
        if level == 1 or level == 2:
            # parse page
            soup = BeautifulSoup(raw_page, 'html.parser')
            # find list of locations
            raw_list = soup.find('div', class_="maxHeight")
            # get first div
            raw_list = raw_list.find('div')
            # get all links in list of locations
            raw_list = raw_list.find_all('a')

            # associate location with ulr
            for item in raw_list:
                url_decoded = quote(item.attrs['href'])
                locations_list[item.get_text()] = "https:" + url_decoded

            for item in locations_list:  # print out locations
                self.app.stdout.write(f"{item}\n")

        # on city level
        if level == 3:
            # parse page
            soup = BeautifulSoup(raw_page, 'html.parser')
            # find list of locations
            raw_list = soup.find('div', class_="mapBotCol")
            raw_list = raw_list.find('div', class_="clearfix")
            # get all links in list of locations
            raw_list = raw_list.find_all('a')
            # associate location with ulr
            for item in raw_list:
                url_decoded = quote(item.attrs['href'])
                locations_list[item.get_text()] = "https:" + url_decoded

            for item in locations_list:  # print out locations
                self.app.stdout.write(f"{item}\n")

        choice = input(f"\nEnter {levels[level]} name:\n")

        # call recursively if not on city level
        if level != 3:

            try:
                location_set = \
                    self.browse_location(level+1, locations_list[choice])
            except KeyError:
                self.logger.error(
                    'Wrong name entered. ' +
                    'Please, restart application and try again')
                sys.exit()
        # get the result
        if level == 3:
            location_set['URL'] = locations_list[choice]
            location_set['Location'] = choice

        return location_set

    def set_location(self, location_set):
        """ Sets Sinoptik location to the config
            :param location_set: URLs and Location given by browse_location
        """

        self.URL = location_set['URL']
        self.Location = location_set['Location']
