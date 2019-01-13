""" Abstract classes for weatherapp project """

import abc
import pathlib
import argparse
import configparser

import config

class Command(abc.ABC):
    """ Base class for commands """

    def __init__(self, app):
        self.app = app

    @staticmethod
    def get_parser():
        parser = parser.ArgumentParser()
        return parser

    @abc.abstractmethod
    def run(self, argv):

        """ I don't understand it's purpose, just copiyng
            Let it be
            Should be overriden
        """

class WeatherProvider(Command):
    """ WeatherProvider abstract class """

    def __init__(self, app):
        super().__init__(app) #отримуємо App з базового класу

        location, url = self._getconfiguration() #отримуємо конфігурацію
        self.location = location
        self.url = url

    def initiate(self, provider_data):
        """ Sets instance variables for config """
        for item in provider_data:
            self.__setattr__(item, provider_data[item])

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
        path = pathlib.Path(self.Cache_path)
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
            if time.time() < self.get_cache_time(URL) + self.Caching_time * 60:
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

    def get_instance_variables(self):
        """ Returns dictionary {self.variable: value} """

        inst_variables = {}

        for item in self.__dict__:
            if item == 'raw_page':
                pass
            else:
                inst_variables[item] = self.__getattribute__(item)

        return inst_variables

    @abc.abstractmethod
    def get_info(self):
        """ Extracts weather info from loaded page using BS4
            returns info in dictionary: Temperature, Condition, RealFeel

            Should be overriden
        """
        pass

    @abc.abstractmethod
    def get_hourly(self):
        """ Gets temperature forecast for next hours

        """
        pass

    @abc.abstractmethod
    def get_next_day(self):
        """ Extracts weather info for next day
        """
        pass
    @abc.abstractmethod
    def get_current_location(self):

        """ Returns current location
        """
        pass

    @abc.abstractmethod
    def browse_location(self, level = 0, URL_location = None):
        """ Browse locations of weather provider
        """

    @abc.abstractmethod
    def set_location(self, location_set):
        """ Sets to the config location """

        @abc.abstractmethod

    def run(self):
        """ Main function that runs WeatherProvider class """
