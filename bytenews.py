# -*- coding: utf-8 -*-
"""
Created on Fri Jul 22 21:18:26 2016

@author: Chaos
"""
from datetime import datetime
from bs4 import BeautifulSoup

import requests
import pyperclip
import re

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

    output = soup.prettify()
    
    forms = soup.find_all('form')
    items = forms[1].find_all('li')
    
    changes = {}    
    
    for item in items:
        print('=============================================================')
        link = item.find_all('a', re.compile('wikilink.*'))     
        print(link[0]['href'])
        spans = item.find_all('span')
        values= []
        for span in spans:
          for strings in span.stripped_strings:
              values.append(strings)
              values.append(1)
              
        if link[0] not in changes:
          changes[link[0]['href']] = values
        else:
            changes[link[0]['href']][1] += values[1]
            changes[link[0]['href']][3] += 1
        
    for c,v in changes.items():   
        print(c)
        print(v)
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
    #output += blog()
    output += '\n\n'

    output = wiki()
    
   # print(output)

    pyperclip.copy(output)


if __name__ == '__main__':
    main()
    