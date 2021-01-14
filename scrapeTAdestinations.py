import requests
import pymysql
import time as timeutils

from bs4 import BeautifulSoup
from lxml import html


conn = pymysql.connect(host='127.0.0.1',
                             user='root',
                             password='root',
                             db='mysql',
                             charset='utf8')
cur = conn.cursor()
cur.execute('USE wikipedia')

def loadUrls():
    cur.execute('SELECT * FROM pages WHERE numpages is NULL') #50267
    pages = cur.fetchall()
    return pages



def insertPageIfNotExists(data):
    cur.execute('SELECT * FROM attractions WHERE url = %s', (data['url']))
    if cur.rowcount == 0:
        try:
            cur.execute('INSERT INTO attractions (url, name, reviews, rating, category) VALUES (%s, %s, %s, %s, %s)', 
            (data['url'], data['name'], data['reviews'], data['rating'], data['category']))
        except:
            try:
                cur.execute('INSERT INTO attractions (url, name, reviews, rating, category) VALUES (%s, %s, %s, %s, %s)', 
                (data['url'] ,'Name error', data['reviews'], data['rating'], data['category']))
            except:
                print(data['url'])
        conn.commit()
        return cur.lastrowid
    else:
        return cur.fetchone()[0]

def updatePageWithNumResults(iden, count):
        try:
            cur.execute('UPDATE pages SET numresults = %s WHERE id = %s', 
            (count, iden))
        except:
            print('error updating count for ' + iden)
        conn.commit()
        return cur.lastrowid

def updatePageWithNumPages(iden, pages):
        try:
            cur.execute('UPDATE pages SET numpages = %s WHERE id = %s', 
            (pages, iden))
        except:
            print('error updating pages for ' + iden)
        conn.commit()
        return cur.lastrowid

def performCrawl(urlCity):

    links = []
    hotel_data = []
    count = 0

    try:
        page_response  = requests.get(urlCity)
    except:
        return

    parser = html.fromstring(page_response.text)
    
    links += parser.xpath('//div[contains(@class,"_1h6gevVw")]')
    links += parser.xpath('//div[contains(@class,"_1baMczO_")]')
    links += parser.xpath('//div[contains(@class,"_25PvF8uO")]')
    links += parser.xpath('//div[contains(@class,"_20eVZLwe")]')
    links += parser.xpath('//div[contains(@class,"_2zqaS_NY")]')
    links += parser.xpath('//a[contains(@class,"__255i5rcQ")]')
    for link in links : 
        XPATH_ATTRACTION_LINK = './/a[@class="_255i5rcQ" or @class="_1QKQOve4" or @class="_3W3bcspL" or @class="_255i5rcQ uTiM3iW0"]/@href'
        raw_attraction_link = link.xpath(XPATH_ATTRACTION_LINK)

        XPATH_REVIEWS  = './/span[@class="reviewCount _16Nxw4iy" or @class="_1DasOrRF" or @class="HLvj7Lh5 _1L-8ZIjh _2s3pPhGm"]//text()'
        raw_no_of_reviews = link.xpath(XPATH_REVIEWS)

        XPATH_RATING = './/svg[@class="_3KcXyP0F" or @class="_3KcXyP0F"]/@title'
        raw_rating = link.xpath(XPATH_RATING)

        XPATH_ATTRACTION_NAME = './/a[@class="_255i5rcQ" or @class="_1QKQOve4" or @class="_3W3bcspL" or @class="_255i5rcQ uTiM3iW0"]//text()'
        raw_attraction_name = link.xpath(XPATH_ATTRACTION_NAME)

        XPATH_CATEGORY = './/span[@class="_21qUqkJx" or @class="_21qUqkJx"]//text()'
        raw_category = link.xpath(XPATH_CATEGORY)

        url = ''.join(raw_attraction_link[0]) if raw_attraction_link else  None
        reviews = ''.join(raw_no_of_reviews).replace("reviews","").replace("review","").replace(",","") if raw_no_of_reviews else 0 
        rating = ''.join(raw_rating).replace('of 5 bubbles','').strip() if raw_rating else None
        
        try:
            if rating is None:
                raw_rating = link.xpath('.//div[@class="ui_poi_review_rating  "]/span/@class')
                rating_tokens = raw_rating[0].split('_')
                rating = float(rating_tokens[3])/10;

            if reviews is not None and int(reviews) < 100:
                continue
    
            if rating is not None and float(rating) < 2:
                continue
        except Exception as e:
           print(e)

        name = ''.join(raw_attraction_name).strip() if raw_attraction_name else None
        category = ''.join(raw_category).strip() if raw_category else None

        data = {
                'name':name,
                'url':url,
                'reviews':reviews,
                'rating':rating,
                'category':category


            }

        if url is None:
            return
            
        pageId = insertPageIfNotExists(data)
        count = count + 1
    return count

pages = loadUrls()
for pageRows in pages:
    page = pageRows[1];

    count = 0;
    
    pageTokens = page.split('-')

    base_url = 'https://www.tripadvisor.com/'  ## we need this to join the links later ##
    main_page = base_url + 'Attractions-' +pageTokens[1] + '-Activities-oa{}-' + pageTokens[2] + '.html'

    try:
        r = requests.get(main_page.format(30))  
    except:
        timeutils.sleep(30)
        performCrawl(urlCity)
    print(str(pageRows[0]) + ':' + main_page)
    soup = BeautifulSoup(r.text, "html.parser")

    try:
        last_page = max([ int(section.text) for section in soup.find_all('a', {'class':'pageNum'}) ])
        updatePageWithNumPages(pageRows[0], last_page)
    except:
        last_page = 1
        updatePageWithNumPages(pageRows[0], -1)

    last_page = 1

    for i in range(0, last_page * 30, 30):
        urlCity = main_page.format(i)
        try:
            print(urlCity)
        except:
            print('error in printing')
        try:
            result = performCrawl(urlCity)
            if result:
                count = count + result

        except Exception as e:
            print(e)
            timeutils.sleep(10)
            result = performCrawl(urlCity)
            if result:
                count = count + result
    updatePageWithNumResults(pageRows[0], count)