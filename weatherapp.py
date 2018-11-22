"""
Test project
"""

from urllib.request import urlopen, Request
from html import escape, unescape

""" Read page from Accuweather """
ACCU_URL = "https://www.accuweather.com/uk/ua/kyiv/324505/weather-forecast/324505"
ACCU_HEAD = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:63.0) Gecko/201'}
ACCU_REQUEST = Request(ACCU_URL, headers = ACCU_HEAD)
ACCU_PAGE = urlopen(ACCU_REQUEST).read()
ACCU_PAGE = ACCU_PAGE.decode('utf-8')

""" Extract an info about weather"""
ACCU_Condition_tag = 'txt : \''
ACCU_TEMP_tag = 'temp_f : \''
ACCU_RealFeel_tag = 'rf : \''
ACCU_Data = {}

"""Condition"""
start = ACCU_PAGE.find(ACCU_Condition_tag)
end = ACCU_PAGE.find(",", start + 1)
ACCU_Data['Condition'] = ACCU_PAGE[start + len(ACCU_Condition_tag):end-1]

"""Temperature"""
start = ACCU_PAGE.find(ACCU_TEMP_tag)
end = ACCU_PAGE.find(",", start + 1)
temp = int(ACCU_PAGE[start + len(ACCU_TEMP_tag):end-1])
ACCU_Data['Temperature'] = (temp - 32) * 5 / 9 #convert to celsius

"""RealFeel"""
start = ACCU_PAGE.find(ACCU_RealFeel_tag)
end = ACCU_PAGE.find(",", start + 1)
ACCU_Data['RealFeel'] = ACCU_PAGE[start + len(ACCU_RealFeel_tag):end-3]

print('\nПоточна погода за даними Accuweather:\n')
print(f"Температура {ACCU_Data['Temperature']:.0f} {unescape('&deg')}C,"
     f"відчувається як {ACCU_Data['RealFeel']} {unescape('&deg')}C,"
     f" на небі - {ACCU_Data['Condition']}\n")

""" Load weather info from RP5 """

RP5_URL = "http://rp5.ua/%D0%9F%D0%BE%D0%B3%D0%BE%D0%B4%D0%B0_%D0%B2_%D0%9A%D0%B8%D1%94%D0%B2%D1%96"
RP5_HEAD = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:63.0) Gecko/201'}
RP5_REQUEST = Request(RP5_URL, headers = RP5_HEAD)
RP5_PAGE = urlopen(RP5_REQUEST).read()
RP5_PAGE = str(RP5_PAGE, encoding = 'utf-8')

RP5_Condition_tags = {'1': "ftab_1_content",
                        '2': "tooltip(this, \'<b>"}
RP5_TEMP_tag = '\"t_0\" style=\"display: block;\">'
RP5_RealFeel_tag = "f_temperature"
RP5_Data = {}

"""Temperature"""
start = RP5_PAGE.find(RP5_TEMP_tag)
end = RP5_PAGE.find("<", start + 1)
RP5_temp = RP5_PAGE[start + len(RP5_TEMP_tag):end-1]
RP5_Data['Temperature'] = RP5_temp

"""Condition"""
start = RP5_PAGE.find(RP5_Condition_tags['1']) #Search in 1 day forecast tab
start = RP5_PAGE.find('</tr', start)
start = RP5_PAGE.find('</tr', start+5) #skip two rows in the table
start = RP5_PAGE.find(RP5_Condition_tags['2'], start)
end = RP5_PAGE.find("</b>", start)
RP5_Data['Condition'] = RP5_PAGE[start + len(RP5_Condition_tags['2']):end]

"""RealFeel"""
start = RP5_PAGE.find(RP5_RealFeel_tag, end)
start = RP5_PAGE.find("<div class=\"t_0\">", start)
end = RP5_PAGE.find("</b>", start)
RP5_Data['RealFeel'] = RP5_PAGE[start + len("<div class=\"t_0\">"):end]

print('\nПоточна погода за даними RP5:\n')
print(f"Температура {unescape(RP5_Data['Temperature'])}C,"
        f" відчувається як {RP5_Data['RealFeel']} {unescape('&deg')}C,"
        f" на небі - {RP5_Data['Condition']}\n")

""" Data from sinoptik"""
SINOPTIK_URL = "https://ua.sinoptik.ua/%D0%BF%D0%BE%D0%B3%D0%BE%D0%B4%D0%B0-%D0%BA%D0%B8%D1%97%D0%B2"
SINOPTIK_HEAD = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:63.0) Gecko/201'}
SINOPTIK_REQUEST = Request(SINOPTIK_URL, headers = SINOPTIK_HEAD)
SINOPTIK_PAGE = urlopen(SINOPTIK_REQUEST).read()
SINOPTIK_PAGE = str(SINOPTIK_PAGE, encoding = 'utf-8')

SINOPTIK_open_tag = "<div class=\"wMain clearfix\">"
SINOPTIK_close_tag = "<div class=\"wDescription clearfix\">"

SINOPTIK_Condition_tags = {'1': "today-time", '2': "alt=\"", 'close_cond_tag': "\""}
SINOPTIK_TEMP_tags = {'temp_open_tag': "today-temp\">",
                        'temp_close_tag': "<"}

SINOPTIK_RealFeel_tags = {"1": "<tr class=\"temperatureSens\">", "RF_open_tag": "cur\" >",
                            "RF_close_tag": "<"}
SINOPTIK_Data = {}
start = SINOPTIK_PAGE.find(SINOPTIK_open_tag)
end = SINOPTIK_PAGE.find(SINOPTIK_close_tag)
SINOPTIK_scrap_page = SINOPTIK_PAGE[start:end]

"""Condition"""
start = SINOPTIK_scrap_page.find(SINOPTIK_Condition_tags['1'])
start = (SINOPTIK_scrap_page.find(SINOPTIK_Condition_tags['2'], start) +
                                    + len(SINOPTIK_Condition_tags['2']))
end = SINOPTIK_scrap_page.find(SINOPTIK_Condition_tags['close_cond_tag'], start)
SINOPTIK_Data['Condition'] = SINOPTIK_scrap_page[start : end]

"""Temperature"""
start = (SINOPTIK_scrap_page.find(SINOPTIK_TEMP_tags['temp_open_tag']) +
                                    + len(SINOPTIK_TEMP_tags['temp_open_tag']))
end = SINOPTIK_scrap_page.find(SINOPTIK_TEMP_tags['temp_close_tag'], start)
SINOPTIK_Data['Temperature'] = SINOPTIK_scrap_page[start : end]

"""RealFeel"""
start = SINOPTIK_scrap_page.find(SINOPTIK_RealFeel_tags['1'])
start = (SINOPTIK_scrap_page.find(SINOPTIK_RealFeel_tags['RF_open_tag'], start) +
                                    + len(SINOPTIK_RealFeel_tags['RF_open_tag']))
end = SINOPTIK_scrap_page.find(SINOPTIK_RealFeel_tags['RF_close_tag'], start)
SINOPTIK_Data['RealFeel'] = SINOPTIK_scrap_page[start : end]

print('\nПоточна погода за даними Sinoptik:\n')
print(f"Температура {unescape(SINOPTIK_Data['Temperature'])},"
        f" відчувається як {unescape(SINOPTIK_Data['RealFeel'])}C,"
        f" на небі - {SINOPTIK_Data['Condition']}\n")
