# -*- coding: utf-8 -*-
"""
Created on Fri Jul 22 21:18:26 2016

@author: Chaos
"""
from datetime import datetime
from bs4 import BeautifulSoup

import requests

def blog():
    ''' Reads feed from bytespeicher.org, extracts article titles,
    dates and links. Stops before last Bytespeicher Notizen.
    '''
    website = requests.get("https://bytespeicher.org/feed/")
    html_source = website.text
    soup = BeautifulSoup(html_source, 'lxml-xml')

    items = soup.channel.find_all('item')
    for item in items:
        title = item.title.string
        date_str_long = item.pubDate.string
        link = item.link.string
        if "Bytespeicher Wochennotizen" in title:
            break
        date = datetime.strptime(date_str_long, '%a, %d %b %Y %H:%M:%S %z')

        print('* ' + title + ' ('+date.strftime('%d %b')+')')
        print(link)


def main():
    ''' call all subfunctions to generate content '''
    blog()


if __name__ == '__main__':
    main()
    