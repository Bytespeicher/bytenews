# -*- coding: utf-8 -*-
"""
Created on Fri Jul 22 21:18:26 2016

@author: Chaos
"""
from datetime import datetime
import re

from bs4 import BeautifulSoup
import requests
import pyperclip

def blog():
    ''' Reads feed from bytespeicher.org, extracts article titles,
    dates and links. Stops before last Bytespeicher Notizen.
    '''
    website = requests.get("https://bytespeicher.org/feed/")
    html_source = website.text
    soup = BeautifulSoup(html_source, 'lxml-xml')

    items = soup.channel.find_all('item')
    output = ""
    for item in items:
        title = item.title.string
        date_str_long = item.pubDate.string
        link = item.link.string
        if "Bytespeicher Wochennotizen" in title:
            break
        date = datetime.strptime(date_str_long, '%a, %d %b %Y %H:%M:%S %z')

        #print('* ' + title + ' ('+date.strftime('%d %b')+')')
        #print(link)

        output += '* ' + title + ' ('+date.strftime('%d %b')+')\n'+link+'\n'

    return output


def wiki():
    ''' Reads changes technikkultur-erfurt.de, extracts changes + comments,
    dates and links. Stops before date of last Bytespeicher Notizen.
    '''
    website = requests.get("https://technikkultur-erfurt.de/start?do=recent")
    html_source = website.text
    soup = BeautifulSoup(html_source, 'lxml')

    forms = soup.find_all('form')
    items = forms[1].find_all('li')
    output = ''

    for item in items:
        output += '* '
        link = item.find_all('a', re.compile('wikilink.*'))
        output += link[0]['href']

        linkdiff = item.find_all('a', 'diff_link')
        spans = item.find_all('span')

        output += " ("
        date_str = list(spans[0].stripped_strings)[0]
        date = datetime.strptime(date_str, '%d.%m.%Y %H:%M')

        comment = list(spans[1].stripped_strings)[0]
        user = list(spans[2].stripped_strings)[0]

        output += date.strftime('%d %b') + ' ' + comment + ' ' + user

        output += ")\n"

        output += 'https://technikkultur-erfurt.de/' + link[0]['href'] + '\n'
        output += 'DELETEME: ' + 'https://technikkultur-erfurt.de/' + linkdiff[0]['href'] + '\n\n'

    #print(soup.body.contents)
    #print(soup.body.div.contents)
    #body.div.main.article.div.div.div.form.div.ul.li)
#    items = soup.channel.find_all('item')
#    output = ""
#    for item in items:
#        title = item.title.string
#        date_str_long = item.pubDate.string
#        link = item.link.string
#        if "Bytespeicher Wochennotizen" in title:
#            break
#        date = datetime.strptime(date_str_long, '%a, %d %b %Y %H:%M:%S %z')
#
#        print('* ' + title + ' ('+date.strftime('%d %b')+')')
#        print(link)
#
#        output += '* ' + title + ' ('+date.strftime('%d %b')+')\n'+link+'\n'
    return output


def main():
    ''' call all subfunctions to generate content '''
    output = '##[BLOG]\n'
    output += blog()
    output += '\n\n'

    output = '##[WIKI]\n'
    output += wiki()
    output += '\n\n'

    print(output)

    pyperclip.copy(output)


if __name__ == '__main__':
    main()
    