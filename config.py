""" Configuration module for weatherapp.py
"""

from urllib.parse import quote, unquote
import pathlib
import configparser

""" Define global params """
weather_providers = {
'ACCU': {'Title': 'Accuweather',
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
working_dir = pathlib.Path.cwd()
Cache_path = pathlib.Path
Caching_time = 60

config = configparser.ConfigParser()
config.optionxform = str
config_path = 'weather_config.ini'

""" End of global params """

""" Config settings and fuctions """

def save_config(config):
    """ Saves config to file with current values """

    for item in weather_providers:
        for key in weather_providers[item]:
            if type(weather_providers[item][key]) == str:
                config[item][key] = unquote(weather_providers[item][key])
            elif type(weather_providers[item][key]) == int:
                config[item][key] = str(weather_providers[item][key])

    with open('weather_config.ini', 'w') as f:
        config.write(f)

def load_config():
    """ Loads configuration
    """
    global weather_providers
    global config_path
    global Cache_path
    global Caching_time

    config.read(config_path)

    #load configuration to the weather_providers dict
    for item in config:
        for key in config[item]:
            if key == 'Caching_time':
                Caching_time = int(config[item][key])
            elif key == 'Cache_path':
                Cache_path = config[item][key]
            elif key == 'Location': #if cyrillic titles than do not urllib.quote
                weather_providers[item][key] = config[item][key]
            else: #if URL
                weather_providers[item][key] = quote(config[item][key], safe='://')

    return config

def restore_config(weather_providers):
    """ Restores config with defaults """

    config['ACCU'] = {}
    config['Sinoptik'] = {}
    config['RP5'] = {}

    for item in weather_providers:
        for key in weather_providers[item]:
            if type(weather_providers[item][key]) == str:
                config[item][key] = unquote(weather_providers[item][key])
            elif type(weather_providers[item][key]) == int:
                config[item][key] = str(weather_providers[item][key])

    """
    config['Cache']['Caching_interval'] = str(Caching_time)
    config['Cache']['Cache_dir'] = 'Cache'
    """
    return config

def initiate_config(config, weather_providers):
    """ Initiates config
        Sets weather_providers and other conf variables
    """
    config = configparser.ConfigParser()
    config.optionxform = str
    path = pathlib.Path(config_path)

    if not path.exists(): #create new config file with defaults
        config = restore_config(weather_providers)
        save_config(config)
    else:
        config = load_config()

    return config

def set_config(title, variables, weather_providers):
    """ Sets new config variables
        title - title of weather provider
        variables - provider variables
        weather_providers - output
    """

    if title == 'Accuweather':
        for item in variables:
            weather_providers['ACCU'][item] = variables[item]
    elif title == 'RP5':
        for item in variables:
            weather_providers['RP5'][item] = variables[item]
    elif title == 'Sinoptik':
        for item in variables:
            weather_providers['Sinoptik'][item] = variables[item]

    return weather_providers

config = initiate_config(config, weather_providers)

if __name__ == "__main__":
    pass
