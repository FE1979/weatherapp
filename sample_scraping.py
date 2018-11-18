"""
JUst scraping
"""

from urllib.request import urlopen, Request

URL = "http://example.webscraping.com/"
HEAD = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:63.0) Gecko/201'}

REQ = Request(URL, headers = HEAD)
Response = urlopen(REQ).read()
Response = Response.decode('utf-8')

""" Find a table with countries"""
Table_start = Response.find('<table>')
Table_end = Response.find('</table', Table_start)
Content = Response[Table_start : Table_end]

Current_position = 0
Countries = []

""" Let take a country and delete it from Content"""
while Content:
    Current_position = Content.find('/> ', Current_position) + 3 #Plus lenght of '/> ' - starting point
    Country_name_end = Content.find('</a>', Current_position) #end point of Country's name
    if Country_name_end == -1: #If no ending tag found - exit
        break
    Countries.append(Content[ Current_position : Country_name_end ]) #add it to the list
    Content = Content[Country_name_end:] #remove all before other countries
    Current_position = 0 #Let start from the beginning
    pass

print(Countries)
