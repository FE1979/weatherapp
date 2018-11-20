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
print(f"Температура {ACCU_Data['Temperature']:.0f} {unescape('&deg')}C, відчувається як {ACCU_Data['RealFeel']}, на небі - {ACCU_Data['Condition']}\n")

a = input('RP5')

""" Load weather info from RP5 """

RP5_URL = "http://rp5.ua/%D0%9F%D0%BE%D0%B3%D0%BE%D0%B4%D0%B0_%D0%B2_%D0%9A%D0%B8%D1%94%D0%B2%D1%96"
RP5_HEAD = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:63.0) Gecko/201'}
RP5_REQUEST = Request(RP5_URL, headers = RP5_HEAD)
RP5_PAGE = urlopen(RP5_REQUEST).read()
RP5_PAGE = str(RP5_PAGE)

RP5_Condition_tag = ''
RP5_TEMP_tag = '\"t_0\" style=\"display: block;\">'
RP5_RealFeel_tag = ''
RP5_Data = {}

"""Temperature"""
start = RP5_PAGE.find(RP5_TEMP_tag)
end = RP5_PAGE.find("<", start + 1)
RP5_temp = RP5_PAGE[start + len(RP5_TEMP_tag):end-1]
RP5_Data['Temperature'] = RP5_temp
RP5_Data['RealFeel'] = RP5_temp
RP5_Data['Condition'] = RP5_temp

print('\nПоточна погода за даними RP5:\n')
print(f"Температура {unescape(RP5_Data['Temperature'])}C, відчувається як {RP5_Data['RealFeel']}, на небі - {RP5_Data['Condition']}\n")

#print(unescape(RP5_temp))
