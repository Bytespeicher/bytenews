# -*- coding: utf-8 -*-
"""
Created on Fri Jul 22 21:18:26 2016

@author: Chaos
"""
from datetime import datetime
import re
import locale

from bs4 import BeautifulSoup
import requests
import pyperclip
import pytz


TZ = pytz.timezone('Europe/Berlin')

def getStopDate():
    ''' reads the category feed for bytespeicher notizen and gets the last publication date '''  
    
    website = requests.get('https://bytespeicher.org/category/bytespeicher-notizen/feed/')
    html_source = website.text
    soup = BeautifulSoup(html_source, 'lxml-xml')
    
    datexml = soup.find('item').find('pubDate') 
    
    locale.setlocale(locale.LC_TIME, 'eng_us')
    stop = datetime.strptime(datexml.string, '%a, %d %b %Y %H:%M:%S %z')
    
    return stop
    
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


def wiki(stop_date):
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
        
        if '/freifunk:' in link[0]['href']:
            stub = output.rfind('*')
            output = output[:stub]
            continue
        
        output += link[0]['href']

        linkdiff = item.find_all('a', 'diff_link')
        spans = item.find_all('span')

        output += " ("
        date_str = list(spans[0].stripped_strings)[0]
        date = datetime.strptime(date_str, '%d.%m.%Y %H:%M')

        if TZ.localize(date) < stop_date:
            stub = output.rfind('*')
            output = output[:stub]
            break

        comment = list(spans[1].stripped_strings)[0]
        if comment == "– gelöscht":
            stub = output.rfind('*')
            output = output[:stub]
            continue

        user = list(spans[2].stripped_strings)[0]

        output += date.strftime('%d %b') + ' ' + comment + ' ' + user

        output += ")\n"

        output += 'https://technikkultur-erfurt.de/' + link[0]['href'] + '\n'

#ToDo: sumarize als unreported changes into one difflink
        diffwebsite = requests.get("https://technikkultur-erfurt.de/" + link[0]['href'] + '?do=revisions' )
        diffhtml_source = diffwebsite.text
        print("https://technikkultur-erfurt.de/" + link[0]['href']  + '?do=revisions')
        
        pyperclip.copy(diffhtml_source)
        
        diffsoup = BeautifulSoup(diffhtml_source, 'lxml')

        changes = diffsoup.find_all('div', 'li' )
        difflink = ''
        for i, c in enumerate(changes):
            date = c.span.string
            if datetime.strptime(date.strip(), '%d.%m.%Y %H:%M') < LAST_NEWSLETTER:
                break
            if i != 0:
                difflink = c.find('a', 'diff_link')['href']
                        
        output += 'DELETEME: ' + 'https://technikkultur-erfurt.de/'+ difflink +'\n\n'

    return output


def redmine(stop_date):
    ''' read redmine site to get tickets modified since last notizen '''

    output = ""
    
    website = requests.get("https://redmine.bytespeicher.org/projects/bytespeicher/issues?c%5B%5D=tracker&c%5B%5D=status&c%5B%5D=priority&c%5B%5D=subject&c%5B%5D=assigned_to&c%5B%5D=updated_on&f%5B%5D=&group_by=&set_filter=1&sort=updated_on%3Adesc%2Cid%3Adesc&utf8=%E2%9C%93")
    html_source = website.text
    soup = BeautifulSoup(html_source, 'lxml')
    
    t_list = soup.find('tbody')

    links = [c['href'] for c in t_list.find_all('a')]
    cat = [c.string for c in t_list.find_all("td", "tracker")]
    stat = [c.string for c in t_list.find_all("td", "status")]
    title = [c.a.string for c in t_list.find_all("td", "subject")]
    user = [c.a.string if c.a else "" for c in t_list.find_all("td", "assigned_to")]
    dates = [datetime.strptime(c.string, '%d.%m.%Y %H:%M') for c in t_list.find_all("td", "updated_on")]
    
    all_tickets = list(zip(links,cat, stat, title, user, dates))
    
    for t in all_tickets:
        output += "* " + t[1] + ': ' + t[3] + ' ' + t[2] + ' (' + t[4] + ', ' + t[5].strftime('%d %b') + ')\n'
        output += "https://redmine.bytespeicher.org" + t[0] + '\n'
        if TZ.localize(t[5]) < stop_date:
            stub = output.rfind('*')
            output = output[:stub]
            break
#    pyperclip.copy(html_source)    
    
    return output


def is_not_more_tag(attr):
    if attr == '#':
        return False
    else:
        return True



def mail(stop_date):
    ''' reads the mailman archives to get active discussions since last publication '''    
    output = ""
    
    
    website = requests.get("https://lists.bytespeicher.org/archives/list/bytespeicher%40lists.bytespeicher.org/")
    html_source = website.text
    soup = BeautifulSoup(html_source, 'lxml')
#    pyperclip.copy(html_source)

    section = soup.find('section', id='most-recent')
    fields = section.find_all('a', href=is_not_more_tag)
    import pprint
    pp = pprint.PrettyPrinter(indent=4)
#    pp.pprint([a if not a.h5 else '' for a in fields])

    links = [a['href'] for a in fields]
    topics = [a.h5 for a in fields]
    datestr = [list(a.div.stripped_strings)[0].replace('nachm.', '').replace('vorm.', '')[:-1] for a in fields]
    
    pp.pprint(datestr)    
    locale.setlocale(locale.LC_TIME, 'deu_deu')

    dates = [datetime.strptime(s, '%a %b %d, %H:%M') for s in datestr]
    locale.setlocale(locale.LC_TIME, 'eng_us')

#    pp.pprint([a if a else 'FAILFAILFAIL=======================================' for a in topics])
    
    all_mail = list(zip(links, topics, dates))
    
    for m in all_mail:
#        output += "* " + m[1] + ': ' + m[3] + ' ' + m[2] + ' (' + m[4] + ', ' + m[5].strftime('%d %b') + ')\n'
#        output += "https://redmine.bytespeicher.org" + m[0] + '\n'
        output += "* " + list(m[1].stripped_strings)[1] + '(' + m[2].strftime('%d %b') + ')\n'
        output += 'https://lists.bytespeicher.org' + m[0] + '\n'
#        if TZ.localize(m[5]) < stop_date:
#            stub = output.rfind('*')
#            output = output[:stub]
#            break
    return(output)


def main():
        
    stop_date = getStopDate()

    ''' call all subfunctions to generate content '''
    output = '##[BLOG]\n'
#    output += blog()
#    output += '\n\n'
#
#    output += '##[WIKI]\n'
#    output += wiki(stop_date)
#    output += '\n\n'
#
#    output += '##[REDMINE]\n'
#    output += redmine(stop_date)
#    output += '\n\n'

    output += '##[MAILINGLISTE]\n'
    output += mail(stop_date)
    output += '\n\n'

    print(output)

#    pyperclip.copy(output)

    #ToDo: write directly to etherpad


if __name__ == '__main__':
    main()
    