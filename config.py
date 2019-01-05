""" Configuration module for weatherapp.py
"""

from urllib.parse import quote, unquote
import pathlib
import configparser

import decorators

""" Define global params """
#WEATHER_PROVIDERS used as default values for first start or settings container
WEATHER_PROVIDERS = {
'Accuweather': {'Title': 'Accuweather',
        'URL': "https://www.accuweather.com/uk/ua/kyiv/324505/weather-forecast/324505",
        'URL_hourly': "https://www.accuweather.com/uk/ua/kyiv/324505/hourly-weather-forecast/324505",
        'URL_next_day': "https://www.accuweather.com/uk/ua/kyiv/324505/daily-weather-forecast/324505?day=2",
        'Location': 'Київ',
        'URL_locations': "https://www.accuweather.com/uk/browse-locations",
        'Cache_path': str(pathlib.Path.cwd() / 'Cache'),
        'Caching_time': 60
        },
'RP5': {'Title': 'RP5',
        'URL': "http://rp5.ua/" + quote("Погода_в_Києві"),
        'Location': 'Київ',
        'URL_locations': "http://rp5.ua/" + quote("Погода_в_світі"),
        'Cache_path': str(pathlib.Path.cwd() / 'Cache'),
        'Caching_time': 60
        },
'Sinoptik': {'Title': 'Sinoptik',
        'URL': "https://ua.sinoptik.ua/" + quote("погода-київ"),
        'Location': 'Київ',
        'URL_locations': "https://ua.sinoptik.ua/" + quote("погода-європа"),
        'Cache_path': str(pathlib.Path.cwd() / 'Cache'),
        'Caching_time': 60
        }
}

ACTUAL_WEATHER_INFO = {}
ACTUAL_PRINTABLE_INFO = {}
WORKING_DIR = pathlib.Path.cwd()
CACHING_TIME = 60

CONFIG = configparser.ConfigParser()
CONFIG.optionxform = str
CONFIG_PATH = 'weather_config.ini'

""" End of global params """

""" Config settings and fuctions """

def write_config(config):
    """ writes WEATHER_PROVIDERS attributes to config """

    for item in WEATHER_PROVIDERS:
        config[item] = {}
        for key in WEATHER_PROVIDERS[item]:
                config[item][key] = unquote(str(WEATHER_PROVIDERS[item][key]))

    return config

def save_config(config):
    """ Saves config to file with current values """

    config = write_config(config)

    with open('weather_config.ini', 'w') as f:
        config.write(f)

def load_config(config):
    """ Loads configuration to WEATHER_PROVIDERS
    """
    weather_providers = {}

    config.read(CONFIG_PATH)

    #load configuration to the weather_providers dict
    for item in config:
        weather_providers[item] = {}
        for key in config[item]:
            if key == 'Caching_time':
                weather_providers[item]['Caching_time'] = int(config[item][key])
            elif key == 'Location': #if cyrillic titles than do not urllib.quote
                weather_providers[item][key] = config[item][key]
            else: #if URL
                weather_providers[item][key] = quote(config[item][key], safe="""://?=\ """)

    return weather_providers

def restore_config(config):
    """ Restores config with defaults """
    """
    config['Accuweather'] = {}
    config['Sinoptik'] = {}
    config['RP5'] = {}
    """

    config = write_config(config)

    return config

@decorators.show_variables
def initiate_config(config):
    """ Initiates config
        Sets weather_providers and other conf variables
    """
    weather_providers = {}
    path = pathlib.Path(CONFIG_PATH)

    if not path.exists(): #create new config file with defaults
        config = restore_config(config)
        save_config(config)
    else:
        weather_providers = load_config(config)

    return config, weather_providers

def set_config(title, variables, weather_providers):
    """ Sets new config variables
        title - title of weather provider
        variables - provider variables
        weather_providers - output
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

CONFIG, WEATHER_PROVIDERS = initiate_config(CONFIG)

if __name__ == "__main__":
    pass
