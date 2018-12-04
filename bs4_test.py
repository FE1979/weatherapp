from urllib.request import urlopen, Request
from bs4 import BeautifulSoup

def get_raw_page(URL):
    """
    Loads a page from given URL
    """
    HEAD = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:63.0) Gecko/201'}
    INFO_REQUEST = Request(URL, headers = HEAD)
    PAGE = urlopen(INFO_REQUEST).read()
    PAGE = str(PAGE, encoding = 'utf-8')

    return PAGE

URL = "https://www.accuweather.com/uk/ua/kyiv/324505/weather-forecast/324505"

page = get_raw_page(URL)
soup = BeautifulSoup(page, 'html.parser')

"""Solution for ACCUWEATHER"""
current_cond_div = soup.find('div', class_='bg bg-s s') #find block with curr condition
temperature = str(current_cond_div.find('span', class_='large-temp').string) #temperature and convert it to string type
Condition = str(current_cond_div.find('span', class_='cond').string) #condition
RealFeel = str(current_cond_div.find('span', class_='realfeel').string) #RealFeel
RealFeel = RealFeel[10:] #remove word 'RealFeel' from it

print(temperature, RealFeel, Condition)


"""
for item in soup.select('div'):
    if item['class'] == "bg bg-s s":
        print(item.children)
"""


"""
for item in soup.find_all('span'):
    print(f'new -> {item.attrs}')
"""
"""
p_list = list(soup.find_all('p'))
for i in p_list:
    print(i)

for i in soup.find_all('p'):
    print(i.attrs)
"""
