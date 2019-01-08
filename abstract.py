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

class Configure(Command):

    pass

class WeatherProvider(Command):
    """ WeatherProvider abstract class """

    def __init__(self, app):
        super().__init__(app) #отримуємо App з базового класу

        location, url = self._getconfiguration() #отримуємо конфігурацію
        self.location = location
        self.url = url

    @abc.abstractmethod
    def get_name(self):
        """ Provider name """

    @abc.abstractmethod
    def get_default_location(self):
        """ default location name """

    @abc.abstractmethod
    def get_default_url(self):
        """ Default location url """

    @abc.abstractmethod
    def configurate(self):
        """ Performs provider configuration """

    @abc.abstractmethod
    def get_weather_info(self, content):
        """ Collects weather information """

    @staticmethod
    def get_configuration_file():
        """ Path to configuration file """
        return Path.home / config.CONFIG_PATH

    def _get_configuration(self):
        """ Returns configured location name and url
            Raise 'ProviderConfigurationError' if configuration is
            broken or wasn't found
        """

        name = self.get_default_location()
        url = self.get_default_url()
        confguration = configparser.ConfigParser()

        try:
            configuration.read(self.get_configuration_file())
        except configparser.Error:
            print(f"Bad configuration file."
                  f"Please reconfigurate your provider: {self.get_name()"})

        if self.get_name() in configuration.sections():
            location_config = configuration[self.get_name()]
            name, url = location_config['name'], location_config['url']

        return name, url

    def save_configuration(self, name, url):
        """ Save selected location to configuration file """

        parser = configparser.ConfigParser()
        config_file = self.get_configuration_file()

        if config_file.exists():
            parser.read(config_file)

        parser[self.get_name()] = {'name': name, 'url': url}
        with open(config_file, 'w') as configfile:
            parser.write(configfile)

    @staticmethod
    def get_request_headers():
        """ Return custom headers for url requests """
        return {'User-Agent': config.FAKE_MOZILLA_AGENT}

    @staticmethod
    def get_url_hash(url):
        """ Generate url hash """
        return hashlib.md5(url.encode('utf-8')).hexdigest()

    @staticmethod
    def get_cache_directory():
        """ Return home directory for cache file """
        return Path.home() / config.CACHE_DIR

    def save_cache():
        pass

    def run(self, argv):
        """ Run provider """
        content = self.get_raw_page(self.url)
        return self.get_info(content)
