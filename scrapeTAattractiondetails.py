import requests
import pymysql
import time as timeutils
import re
import urllib.parse as urlparse

from datetime import datetime, timedelta
from lxml import html, etree


conn = pymysql.connect(host='127.0.0.1',
                             user='root',
                             password='root',
                             db='mysql',
                             charset='utf8')

cur = conn.cursor()
cur.execute('USE itinerarygen')
now = datetime.now()
formatted_now = now.strftime('%Y-%m-%d %H:%M:%S')

def loadAttractionUrlsForScraping(days_since_scraped):
    """Retrieve the list of attraction URLs that has not been scraped within the previous number of days
    specified by days_since_scraped.
    """
    inc_date = now - timedelta(days=days_since_scraped)
    formatted_date = inc_date.strftime('%Y-%m-%d %H:%M:%S')
    cur.execute('SELECT * FROM attractions WHERE url is not null and (modified is null or modified < %s) LIMIT 100', (formatted_date))
    pages = cur.fetchmany(100)
    return pages

def shouldPageBeCrawled(page):
    """Filter the attractions whose details need to be scraped. Only those meeting the criteria of
    number of reviews and the rating are scraped.
    """
    reviews = page[3];
    rating = page[4];
    try:
        if reviews is None or reviews == '0':
            print('here')
            return True
        if rating is None or rating == '0':
            return True
        if int(reviews) < 200:
            return False
        if float(rating) < 3.9:
            return False
        if int(reviews) < 400 and float(rating) < 4.9:
            return False
        if int(reviews) < 800 and float(rating) < 4.4:
            return False
    except:
        return False

    return True
    
def updatePageNotCrawled(iden):
    """Update modified date to indicate crawl attempt date."""
    cur.execute('UPDATE attractions SET modified = %s WHERE id = %s', (formatted_now, iden))
    conn.commit()

def updateAttraction(data):
    """Update attraction entry with details inc city, country, coordinates, etc."""
    cur.execute('UPDATE attractions SET modified = %s, city =  %s, country = %s, latitude = %s, longitude = %s, reviews = %s, rating = %s WHERE id = %s', 
        (formatted_now, data['city'], data['country'], data['latitude'], data['longitude'], data['reviews'], data['rating'], data['id']))
    conn.commit()
    return cur.lastrowid

def performCrawl(page):
    """Crawl the individual page for TripAdvisor Things to Do  for details such as coordinates, 
    ratings and reviews"""
    base_url = 'https://www.tripadvisor.com' 
    pageToCrawl = base_url + page[1]

   try:
        page_response  = requests.get(pageToCrawl)
    except:
        timeutils.sleep(30)
        performCrawl(page)

    parser = html.fromstring(page_response.text)

    country = re.findall('grandparent_name":"[A-za-z\s\-\.]*',page_response.text)[1]
    country = country.replace('grandparent_name":"','')

    coords = re.findall('"coords":"[\-]*[0-9]*\.[0-9]*,[\-]*[0-9]*\.[0-9]*',page_response.text)[1]
    coords = coords.replace('"coords":"', "")
    coordsTokens = coords.split(',')
    latitude = coordsTokens[0]
    longitude = coordsTokens[1]

    city = re.findall('"parent_name":"[A-za-z\s\-\.]*',page_response.text)[1]
    city = city.replace('"parent_name":"','')

    if page[2] is None or page[2] == "":
        name =  parser.xpath('//div[contains(@class,"ui_header h1")]//text()')
    else:
        name = page[2]

    reviews = page[3]
    rating = page[4]
    if page[3] is None or page[3] == '0':
            XPATH_REVIEWS  = './/span[@class="_3WF_jKL7 _1uXQPaAr" or @class="_1DasOrRF" or @class="HLvj7Lh5 _1L-8ZIjh _2s3pPhGm"]//text()'
            raw_no_of_reviews = parser.xpath(XPATH_REVIEWS)
            reviews = ''.join(raw_no_of_reviews).replace("reviews","").replace("Review","").replace(",","").replace("Reviews","") if raw_no_of_reviews else 0 
    else:
            reviews = page[3]

    rating = page[4]
    try:
        if rating is None:
                raw_rating = parser.xpath('//div[contains(@class,"_1NKYRldB")]/span/@class')
                rating_tokens = raw_rating[0].split('_')
                rating = float(rating_tokens[3])/10;
    except:
        rating = 0

    try:
            if reviews == '0' or rating is None:
                updatePageNotCrawled(page[0])
                return

            if reviews is not None and int(reviews) < 100:
                updatePageNotCrawled(page[0])
                return
    
            if rating is not None and float(rating) < 2:
                updatePageNotCrawled(page[0])
                return
    except Exception as e:
           print(e)

    data = {
            'id':page[0],
            'city':city,
            'country':country,
            'latitude':latitude,
            'longitude':longitude,
            'name':name,
            'reviews':reviews,
            'rating':rating
        }

    print(data)
    pageId = updateAttraction(data)


while True:
    attraction_urls = loadAttractionUrlsForScraping(180)
    for url in attraction_urls:

        if shouldPageBeCrawled(url) == False:
            updatePageNotCrawled(url[0])

        else:
            try:
                performCrawl(url)
            except:
                timeutils.sleep(10)
                continue

