"""
Test project
"""

from urllib.request import urlopen, Request

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
print(f"Температура {ACCU_Data['Temperature']:.0f}, відчувається як {ACCU_Data['RealFeel']}, на небі - {ACCU_Data['Condition']}\n")
