from urllib.request import urlopen
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

import re
import pymysql
from random import shuffle
from lxml import html,etree

import requests
import pymysql
import time as oneTime

conn = pymysql.connect(host='127.0.0.1',
                             user='root',
                             password='root',
                             db='mysql',
                             charset='utf8')
cur = conn.cursor()
cur.execute('USE itinerarygen')
pages = []
now = datetime.now()
formatted_now = now.strftime('%Y-%m-%d %H:%M:%S')

def insertPageIfNotExists(url):
    cur.execute('SELECT * FROM hw_countrylinks WHERE url = %s', (url))
    if cur.rowcount == 0:
        cur.execute('INSERT INTO hw_countrylinks (url) VALUES (%s)', (url))
        conn.commit()
        return cur.lastrowid
    else:
        return cur.fetchone()[0]

def insertHotelIfNotExists(data):
    cur.execute('SELECT * FROM hw_hotels WHERE url = %s', (data['url']))
    if cur.rowcount == 0:
        try:
            cur.execute('INSERT INTO hw_hotels (url, name, reviews, rating, latitude, longitude, price,city, country) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)', 
            (data['url'], data['name'], data['reviews'], data['rating'], data['latitude'], data['longitude'], data['price'], data['city'], data['country']))
        except Exception as e:
            print(e)
        conn.commit()
        return 
    else:
        try:
            cur.execute('UPDATE hw_hotels SET name = %s, reviews = %s, rating =%s, latitude =%s, longitude =%s, price =%s,city =%s, country =%s WHERE url = %s', 
            (data['name'], data['reviews'], data['rating'], data['latitude'], data['longitude'], data['price'], data['city'], data['country'], data['url']))
        except Exception as e:
            print(e)
        conn.commit()
        return 

def insertAttraction(data):
    cur.execute('UPDATE attractions SET modified = %s, city =  %s, country = %s, latitude = %s, longitude = %s, reviews = %s, rating = %s WHERE id = %s', 
        (formatted_now, data['city'], data['country'], data['latitude'], data['longitude'], data['reviews'], data['rating'], data['id']))
    conn.commit()
    return cur.lastrowid

def loadPages():
    inc_date = now - timedelta(days=180)
    formatted_date = inc_date.strftime('%Y-%m-%d %H:%M:%S')
    cur.execute('SELECT * FROM hw_countrylinks where id < 62 and id >= 49')
    pages = cur.fetchall()
    return pages

def insertLink(fromPageId, toPageId):
    cur.execute('SELECT * FROM links WHERE fromPageId = %s '
    'AND toPageId = %s', (int(fromPageId), int(toPageId)))
    if cur.rowcount == 0:
        cur.execute('INSERT INTO links (fromPageId, toPageId) VALUES (%s, %s)',
        (int(fromPageId), int(toPageId)))
        conn.commit()

def getCountryLinks(pageUrl):
    links = []
 

    html = urlopen(pageUrl)
    print(pageUrl)
    bs = BeautifulSoup(html, 'html.parser')
    #print(bs)
    targetPages = bs.findAll('a', href=re.compile('(/hostels/)'))
    for targetPage in targetPages:
        print(targetPage)
        targetPage = targetPage.attrs['href']
        insertPageIfNotExists(targetPage)

def performCrawl(page):
    links = []
    hotel_data = []
    count = 0
    print(page[1])

    try:
        page_response  = requests.get(page[1])
    except Exception as e:
        print(e)
        return
    parser = html.fromstring(page_response.text)
    
    links += parser.xpath('//div[contains(@class,"cityrow")]')
    for link in links : 

        XPATH_ATTRACTION_LINK = './/span[@class="propname"]/a/@href'
        raw_attraction_link = link.xpath(XPATH_ATTRACTION_LINK)
        url = ''.join(raw_attraction_link[0]) if raw_attraction_link else  None
        print(url)

        XPATH_RATING = './/span[@class="cityrating"]//text()'
        raw_rating = link.xpath(XPATH_RATING)
        rating = ''.join(raw_rating) if raw_rating else '0'
        print(rating)

        XPATH_ATTRACTION_NAME = './/span[@class="propname"]/a//text()'
        raw_attraction_name = link.xpath(XPATH_ATTRACTION_NAME)
        name = ''.join(raw_attraction_name).strip() if raw_attraction_name else None
        print(name)

        XPATH_ATTRACTION_PRICE = './/span[@class="topcPrice"]//text()'
        raw_attraction_price = link.xpath(XPATH_ATTRACTION_PRICE)
        price = ''.join(raw_attraction_price).replace("PHP","").strip() if raw_attraction_price else None
        print(price)

        try: 
            if rating is not None and float(rating) < 4:
                continue

            if price is not None and float(price) > 2000:
                continue
        except Exception as e:
           print(e)

        try:
            page_hostel_details  = requests.get(url)
            parser2 = html.fromstring(page_hostel_details.text)
        

            latitude = re.findall('"latitude": "[\-]*[0-9]*\.[0-9]*",',page_hostel_details.text)[0]
            longitude = re.findall('"longitude": "[\-]*[0-9]*\.[0-9]*"',page_hostel_details.text)[0]
            reviews = re.findall('"ratingCount": "[0-9]*',page_hostel_details.text)[2]

            latitude = latitude.replace('"latitude": "',"").replace('"', "").replace(",", "")
            longitude = longitude.replace('"longitude": "',"").replace('"', "")
            reviews = reviews.replace('"ratingCount": "',"")
            if int(reviews) < 8:
                continue
            
            city = re.findall('"addressLocality": "[A-Za-z\-\s]*',page_hostel_details.text)[0]
            city = city.replace('"addressLocality": "',"")
            country = re.findall('"addressCountry": "[A-Za-z\-\s]*',page_hostel_details.text)[0]
            country = country.replace('"addressCountry": "',"")


        except Exception as e:
            print(e)
       
        data = {
                'name':name,
                'url':url,
                'reviews':reviews,
                'rating':rating,
                'price':price,
                'latitude': latitude,
                'longitude' :longitude,
                'city':city,
                'country':country
            }
        print(data)
        if url is None:
            continue
            
        pageId = insertHotelIfNotExists(data)
        count = count + 1
    return count
 
for page in loadPages(): 
    print(page)
    try:
        performCrawl(page)
    except Exception as e:
        print(e)
        continue
cur.close()
conn.close()
