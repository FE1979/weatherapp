""" Abstract classes for weatherapp project
    Manager: class for managers
    Command: command class
    WeatherProvider: provider class, child of Command
    Formatter: print-out class
"""

from urllib.request import urlopen, Request
from urllib.parse import quote, unquote
from urllib import parse
from bs4 import BeautifulSoup
from html import escape, unescape

import os
import abc
import pathlib
import hashlib
import time
import argparse
import configparser
import logging

from config import config


class Manager(abc.ABC):
    """ Abstract class for Command or Provider managers """

    @abc.abstractmethod
    def add(self, name, command):
        """ Adds command or provider to container
            :param name: Command or Manager name/title
            :param command: Command or Manager instance

            Should be overriden
        """

    @abc.abstractmethod
    def get(self, name):
        """ Gets command or provider
            :param name: Command or Manager name/title

            Should be overriden
        """


class Command(abc.ABC):
    """ Base class for application commands """

    def __init__(self, app):
        """ Initialize command
            :param app: application instance
        """

        self.app = app

    @staticmethod
    def get_parser():
        """ Returns CLI arguments parser """

        parser = parser.ArgumentParser()
        return parser

    @abc.abstractmethod
    def run(self, argv):
        """ Runs Command
            :param argv: remaining CLI arguments

            Should be overriden
        """


class WeatherProvider(Command):
    """ WeatherProvider abstract class """

    def __init__(self, app):
        """ Initialize Provider
            :param app: application instance
        """

        super().__init__(app)

        self.initiate()  #set Provider vars from config

    def initiate(self):
        """ Sets instance variables from config """

        for item in config.WEATHER_PROVIDERS[self.title]:
            self.__setattr__(item, config.WEATHER_PROVIDERS[self.title][item])

        # RP5 and Sinoptik have same URLs for hourly and next day weather info
        if self.title in ('RP5', 'Sinoptik'):
            self.URL_hourly = self.URL
            self.URL_next_day = self.URL

        self.logger = self._get_logger(self.title, self.app.args.verbosity)

    @staticmethod
    def _get_logger(title, verbose_lvl):
        """ Gets looger forr application
            :param verbose_lvl: logger verbosity level, CLI argument
        """

        logger = logging.getLogger(title)
        console = logging.StreamHandler()

        if verbose_lvl == 1:
            logger.setLevel(logging.INFO)
            console.setLevel(logging.INFO)
        elif verbose_lvl == 2:
            logger.setLevel(logging.DEBUG)
            console.setLevel(logging.DEBUG)
        else:
            logger.setLevel(logging.WARNING)
            console.setLevel(logging.WARNING)

        fmt = logging.Formatter(
                            '%(asctime)s %(name)s %(levelname)s %(message)s')
        console.setFormatter(fmt)
        logger.addHandler(console)

        return logger

    def get_raw_page(self, URL, force_reload = False):
        """ Loads a page from given URL
            :param URL: web page address
            :param force_reload: load from web if True or from cache instead
            :return PAGE: loaded web page
            :rtype: string
        """

        if not self.valid_cache(URL) or force_reload:

            HEAD = {'User-Agent':
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:63.0) Gecko/201'}
            INFO_REQUEST = Request(URL, headers = HEAD)
            PAGE = urlopen(INFO_REQUEST).read()

            self.save_cache(PAGE, URL)

        else:
            PAGE = self.load_cache(URL)

        PAGE = str(PAGE, encoding = 'utf-8')

        return PAGE

    def get_cache_file_path(self, URL):
        """ Gets cache file full path
            :param URL:  web page address
            :return: cache file path
            :rtype: pathlib.Path
        """

        filename = hashlib.md5(URL.encode('utf-8')).hexdigest() + '.wbc'
        path = pathlib.Path(config.WEATHER_PROVIDERS['App']['Cache_path'])
        cache_file_path = path.joinpath(filename)

        return cache_file_path

    def save_cache(self, data, URL):
        """ Saves data to cache file in cache directory
            located in application directory
            :param data: loaded web page
            :param URL: web url of loaded page
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
        """ Gets cache file creating time
            :param URL: loaded web page url
            :return: cache creating time
            :rtype: time
        """

        cache_file = self.get_cache_file_path(URL)

        if cache_file.exists():
            cache_time = cache_file.stat().st_mtime
        else:
            cache_time = 0

        return cache_time

    def load_cache(self, URL):
        """ Loads cache for given URL
            :param URL: url of saved in cache web page
            :return: web page
            :rtype: bytes
        """

        cache_file = self.get_cache_file_path(URL)

        with open(cache_file, 'rb') as f:
            PAGE = f.read()

        return PAGE

    def valid_cache(self, URL):
        """ Validates cache
            :param URL: url of saved in cache web page
            :rtype: boolean
        """

        cache_file = self.get_cache_file_path(URL)

        if cache_file.exists():
            cache_time = cache_file.stat().st_mtime
            if time.time() < self.get_cache_time(URL) + self.Caching_time * 60:
                cache_valid = True
            else:
                cache_valid = False

        else:
            cache_valid = False

        return cache_valid

    def get_instance_variables(self):
        """ Returns instance variables
            :return: dictionary {self.variable: value}
        """

        inst_variables = {}

        for item in self.__dict__:
            if item in ['raw_page', 'app']: #exceptions
                pass
            else:
                inst_variables[item] = self.__getattribute__(item)

        return inst_variables

    @abc.abstractmethod
    def get_info(self):
        """ Extracts weather info from loaded page using BS4
            Returns info in dictionary:
            weather_info = {
                'Temperature': # temperature
                'Condition':   # weather condition
                'RealFeel':    # real feel temperature
                }

            Should be overriden
        """
        pass

    @abc.abstractmethod
    def get_hourly(self):
        """ Gets temperature forecast for next hours
            Returns info in dictionary:
            weather_info = {
                'Max': # maximum temperature forecast
                'Min': # minimum temperature forecast
                'Av':  # average temperature forecast
                'Num': # forecast horizon in hours
                }
            Should be overriden
        """
        pass

    @abc.abstractmethod
    def get_next_day(self):
        """ Extracts weather info for next day
            Returns info in dictionary:
            weather_info = {
                'Temperature': # temperature
                'Condition':   # weather condition
                'RealFeel':    # real feel temperature
                }
            Should be overriden
        """
        pass

    @abc.abstractmethod
    def browse_location(self, level = 0, URL_location = None):
        """ Browse locations of weather provider
            :param level: location level. Increases from '0' - continents to
                                                                    '4' - city
            :param URL_location: web page to browse location if needed
            Should be overriden
        """

    @abc.abstractmethod
    def set_location(self, location_set):
        """ Sets to the config location
            :param location_set: list of URLs and Location
            Should be overriden
        """

    def config_location(self):
        """ Configurate location
            Runs browse_location recursively and saves to config
        """

        # show current location
        self.app.stdout.write("Current location\n")
        self.app.stdout.write(f"{self.Location}\n")
        self.app.stdout.write('\n')

        # choose new location
        location_set = self.browse_location()
        self.set_location(location_set)

        # save location to the config
        config.WEATHER_PROVIDERS = config.set_config(self.Title,
                                    self.get_instance_variables(),
                                    config.WEATHER_PROVIDERS)

    def get_cli_args(self):
        """ Parse Provider arguments """

        parser = argparse.ArgumentParser()
        parser.add_argument("-next", help="Next day forecast",
                    action="store_true")  #Provider option
        group = parser.add_mutually_exclusive_group()
        group.add_argument("-f", "--forec",
                            help="Display forecast for next hours",
                            action="store_true")  #Provider option
        group.add_argument("-nf", "--noforec",
                            help="Do not display forecast for next hours",
                            action='store_false')  #Provider option
        parser.add_argument("-refresh", help="Force reloading pages",
                            action="store_true")  #Provider option
        self.args = parser.parse_args(self.app.remaining_args)

    def run(self):
        """ Runs Provider
            :return: weather information and title for output
            :rtype: tuple
        """

        weather_info = {}
        title = self.title
        city = self.Location
        self.get_cli_args()
        refresh = self.args.refresh

        if self.args.next:
            self.raw_page = self.get_raw_page(self.URL_next_day, refresh)
            info_next_day = self.get_next_day()
            weather_info.update(info_next_day)
            title = title + ", прогноз на завтра, " + city

        if not self.args.next:
            self.raw_page = self.get_raw_page(self.URL, refresh)
            weather_info.update(self.get_info())
            title = title + ", поточна погода, " + city
            if self.args.forec:
                self.raw_page = self.get_raw_page(self.URL_hourly, refresh)
                weather_info.update(self.get_hourly())

        return weather_info, title

class Formatter(abc.ABC):
    """ Class for different print-out of weather information
        attributes:
        headers_dict: weather_info keys corresponds with output keys
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


    @abc.abstractmethod
    def print_out():
        """ Retuns printable information
            Should be overriden
        """
        pass
