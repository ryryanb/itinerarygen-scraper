from urllib.request import urlopen
from bs4 import BeautifulSoup

import re
import pymysql
from random import shuffle

conn = pymysql.connect(host='127.0.0.1',
                             user='root',
                             password='root',
                             db='mysql',
                             charset='utf8')
cur = conn.cursor()
cur.execute('USE itinerarygen')
def insertPageIfNotExists(url):
    cur.execute('SELECT * FROM pages WHERE url = %s', (url))
    if cur.rowcount == 0:
        cur.execute('INSERT INTO pages (url) VALUES (%s)', (url))
        conn.commit()
        return cur.lastrowid
    else:
        return cur.fetchone()[0]

def loadPages():
    cur.execute('SELECT * FROM pages')
    pages = [row[1] for row in cur.fetchall()]
    return pages

def insertLink(fromPageId, toPageId):
    cur.execute('SELECT * FROM links WHERE fromPageId = %s '
    'AND toPageId = %s', (int(fromPageId), int(toPageId)))
    if cur.rowcount == 0:
        cur.execute('INSERT INTO links (fromPageId, toPageId) VALUES (%s, %s)',
        (int(fromPageId), int(toPageId)))
        conn.commit()

def getLinks(pageUrl, pages):
    print(pageUrl)
    html = urlopen('https://www.tripadvisor.com.ph{}'.format(pageUrl))
    bs = BeautifulSoup(html, 'html.parser')
    links = bs.findAll('a', {'class':{'city', 'linkText'}})
    links = [link.attrs['href'] for link in links]
    for link in links:
        print(link)
        pageId = insertPageIfNotExists(link)
        if link not in pages:
            pages.append(link)


siteData = [
    ['Europe', 'g4', 1264, 'Europe'],
    ['Asia', 'g2', 545, 'Asia'],
    ['Mexico', 'g150768', 32, 'Mexico'],
    ['United States', 'g191', 441, 'United_States'],
    ['Canada', 'g153339', 54, 'Canada'],
    ['Middle East', 'g21', 24, 'Middle_East'],
    ['South Pacific', 'g8', 66, 'South_Pacific'],
    ['Caribbean', 'g147237', 26, 'Caribbean'],
    ['Central America', 'g291958', 23, 'Central_America'],
    ['Africa', 'g6', 95, 'Africa']
]

existing_pages = loadPages()
for site in siteData:
    for i in range(0, site[2]):
        getLinks('/Hotels-' + site[1] + '-oa' + str(i*20) + '-' + site[3] + '-Hotels.html', existing_pages)
cur.close()
conn.close()