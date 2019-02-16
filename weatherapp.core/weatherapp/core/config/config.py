""" Configuration module for application

    Saves options into next files, located in core directory:
    weather_config.ini:   # application configuration
    providers_conf.json:  # providers configuration

    Defaults:
    WEATHER_PROVIDERS:    # providers defaults; cache path; display type
    PROVIDERS_CONF:       # providers web parsing options

"""

from urllib.parse import quote, unquote
import pathlib
import configparser
import json

import config.decorators

""" Define global params """
# Defaults
WEATHER_PROVIDERS = {
'App': {
        'Cache_path': str(pathlib.Path.cwd() / 'Cache'),
        'Display': 'table'
        },
'Accuweather': {'Title': 'Accuweather',
        'URL': "https://www.accuweather.com" +
                "/uk/ua/kyiv/324505/weather-forecast/324505",
        'URL_hourly': "https://www.accuweather.com" +
                "/uk/ua/kyiv/324505/hourly-weather-forecast/324505",
        'URL_next_day': "https://www.accuweather.com" +
                "/uk/ua/kyiv/324505/daily-weather-forecast/324505?day=2",
        'Location': 'Київ',
        'URL_locations': "https://www.accuweather.com/uk/browse-locations",
        'Caching_time': 60
                },
'RP5': {'Title': 'RP5',
        'URL': "http://rp5.ua/" + quote("Погода_в_Києві"),
        'Location': 'Київ',
        'URL_locations': "http://rp5.ua/" + quote("Погода_в_світі"),
        'Caching_time': 60
        },
'Sinoptik': {'Title': 'Sinoptik',
        'URL': "https://ua.sinoptik.ua/" + quote("погода-київ"),
        'Location': 'Київ',
        'URL_locations': "https://ua.sinoptik.ua/" + quote("погода-європа"),
        'Caching_time': 60
        }
}
# Defaults
PROVIDERS_CONF = {
                'Accuweather': {'Show': True,
                                'Next_day': False,
                                'Next_hours': True},
                'RP5': {'Show': True,
                        'Next_day': False,
                        'Next_hours': True},
                'Sinoptik': {'Show': True,
                        'Next_day': False,
                        'Next_hours': True}
}

ACTUAL_WEATHER_INFO = {}
ACTUAL_PRINTABLE_INFO = {}
WORKING_DIR = pathlib.Path.cwd()
CACHING_TIME = 60

CONFIG = configparser.ConfigParser()
CONFIG.optionxform = str
CONFIG_PATH = 'weather_config.ini'
PROVIDERS_CONF_PATH = 'providers_conf.json'


def restore_providers_conf():
    """ Restores providers configuration file """

    path_providers = pathlib.Path(PROVIDERS_CONF_PATH)

    with open(path_providers, 'w') as conf_file:
        json.dump(PROVIDERS_CONF, conf_file)


def load_providers_conf():
    """ Loads providers configuration
        :return: provider conf loaded from providers_conf.json
        :rtype: dictionary
    """

    path_providers = pathlib.Path(PROVIDERS_CONF_PATH)

    with open(path_providers, 'r') as conf_file:
        providers_configuration = json.load(conf_file)

    return providers_configuration


def write_providers_conf():
    """ Saves to file providers configuration """

    path_providers = pathlib.Path(PROVIDERS_CONF_PATH)

    with open(path_providers, 'w') as conf_file:
        json.dump(PROVIDERS_CONF, conf_file)


def initiate_providers_conf():
    """ Checks if configuration file existed
        if no file creates one with default conf
        Loads configuration from a file at the end
        :return: provider conf loaded from providers_conf.json
        :rtype: dictionary
    """
    path_providers = pathlib.Path(PROVIDERS_CONF_PATH)

    if not path_providers.exists():
        restore_providers_conf()

    providers_configuration = load_providers_conf()

    return providers_configuration


def write_config(config):
    """ Writes WEATHER_PROVIDERS attributes to config
        :param config: ConfigParser instance
        :return: config
        :rtype: ConfigParser instance
    """

    for item in WEATHER_PROVIDERS:
        config[item] = {}
        for key in WEATHER_PROVIDERS[item]:
                config[item][key] = unquote(str(WEATHER_PROVIDERS[item][key]))

    return config


def save_config(config):
    """ Saves config to file with current values
        :param config: ConfigParser instance
    """

    config = write_config(config)
    path = pathlib.Path(CONFIG_PATH)

    with open(path, 'w') as f:
        config.write(f)


def load_config(config):
    """ Loads configuration to WEATHER_PROVIDERS
        :param config: ConfigParser instance
        :return: providers settings
        :rtype: dictionary
    """

    weather_providers = {}

    config.read(CONFIG_PATH)

    # load configuration to the weather_providers dict
    # if no entry - pass. Check config file with is_valid()
    try:
        for item in config:
            weather_providers[item] = {}
            for key in config[item]:
                if key == 'Caching_time':
                    weather_providers[item]['Caching_time'] = \
                        int(config[item][key])
                elif key == 'Location':
                    weather_providers[item][key] = config[item][key]
                # if key is URL apply 'urlib.quote'
                else:
                    weather_providers[item][key] = \
                        quote(config[item][key], safe="""://?=\ """)
    except ValueError:
        pass

    return weather_providers


def restore_config(config):
    """ Restores config with defaults
        :param config: ConfigParser instance
        :return: config
        :rtype: ConfigParser instance
    """

    config = write_config(config)

    return config


def initiate_config(config):
    """ Initiates config
        Sets weather_providers and other conf variables
        :param config: ConfigParser instance
        :return: configuration and providers settings dictionary
        :rtype: tuple
    """

    weather_providers = {}
    path = pathlib.Path(CONFIG_PATH)

    if not path.exists():  # create new config file with defaults
        config = restore_config(config)
        save_config(config)

    weather_providers = load_config(config)

    return config, weather_providers


def set_config(title, variables, weather_providers):
    """ Sets new config variables
        :param title: weather provider title
        :param variables: provider settings
        :param weather_providers: providers settings dictionary
        :return: providers settings
        :rtype: dictionary
    """

    if title == 'Accuweather':
        for item in variables:
            weather_providers['Accuweather'][item] = variables[item]
    elif title == 'RP5':
        for item in variables:
            weather_providers['RP5'][item] = variables[item]
    elif title == 'Sinoptik':
        for item in variables:
            weather_providers['Sinoptik'][item] = variables[item]

    return weather_providers


def is_valid():
    """ Checks config file for existing values in config file
        Should be run after initiate_config() (loaded file)
        :return: False if config file is broken
        :rtype: boolean
    """

    valid_config = True

    # check if values in config exists
    for item in WEATHER_PROVIDERS:
        if item != '':
            for key in WEATHER_PROVIDERS[item]:
                if WEATHER_PROVIDERS[item][key] == "" or \
                    WEATHER_PROVIDERS[item][key] is None:
                        valid_config = False
        else:
            valid_config = False

    for item in PROVIDERS_CONF:
        if item != '':
            for key in PROVIDERS_CONF[item]:
                if PROVIDERS_CONF[item][key] == "" or \
                    PROVIDERS_CONF[item][key] is None:
                        valid_config = False
        else:
            valid_config = False

    return valid_config


CONFIG, WEATHER_PROVIDERS = initiate_config(CONFIG)
PROVIDERS_CONF = initiate_providers_conf()

if __name__ == "__main__":
    pass
