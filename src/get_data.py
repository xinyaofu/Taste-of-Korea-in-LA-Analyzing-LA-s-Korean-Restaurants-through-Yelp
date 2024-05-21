import requests
from urllib.parse import quote
import sqlite3
import re


API_KEY = 'JStjU0QvRKGR6QbifP-Hj063lBU0Gf3cMeUuOsdVcQsLBqzhvRl-6d7jINUHjBo5TmRdJGLFrH2vFKb5P9QULxdPKxCCKzGDdZBkUhHWlETiN5D32qZ7wPpeGBFbZXYx'
API_HOST = 'https://api.yelp.com'
SEARCH_PATH = '/v3/businesses/search'
BUSINESS_PATH = '/v3/businesses/'
headers = {'Authorization': 'Bearer %s' % API_KEY}

connection = sqlite3.connect('../data/raw/restaurants_data.db')
cursor = connection.cursor()
query = '''
    CREATE TABLE IF NOT EXISTS restaurants (
        id TEXT PRIMARY KEY,
        name TEXT,
        location TEXT,
        rating REAL,
        review_count INTEGER,
        price TEXT,
        readable_id TEXT,
        latitude REAL,
        longitude REAL
    )
'''
cursor.execute(query)

query_ = '''
    CREATE TABLE IF NOT EXISTS reviews (
        id TEXT PRIMARY KEY,
        restaurant_id TEXT,
        text TEXT,
        rating INTEGER,
        time_created TEXT,
        FOREIGN KEY (restaurant_id) REFERENCES restaurants (id)
    )
'''
cursor.execute(query_)


def search_business_ids(cursor, offset=0, limit=20, business_ids=[]):
    url = '{0}{1}'.format(API_HOST, quote(SEARCH_PATH.encode('utf8')))
    url_params = {'term': 'korean', 'location': 'Los Angeles', 'offset': offset, 'limit': limit}
    response = requests.get(url, headers=headers, params=url_params)
    businesses = response.json().get('businesses', [])
    total = response.json().get('total', 0)

    for business in businesses:
        readable_id = extract_readable_id(business.get('url', ''))
        latitude = business['coordinates']['latitude'] if 'coordinates' in business else None
        longitude = business['coordinates']['longitude'] if 'coordinates' in business else None
        cursor.execute('''
            INSERT INTO restaurants (id, name, location, rating, review_count, price, readable_id, latitude, longitude) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (business['id'], business['name'], business['location']['address1'], business['rating'],
              business['review_count'], business.get('price', ''), readable_id, latitude, longitude))

    cursor.connection.commit()

    business_ids.extend([business['id'] for business in businesses])

    if offset + limit < total:
        return search_business_ids(cursor, offset + limit, limit, business_ids)
    else:
        return business_ids


def extract_readable_id(url):
    match = re.search(r'/biz/(.*)', url)
    if match:
        return match.group(1)
    return ''


def get_reviews(business_id, cursor):
    business_path = BUSINESS_PATH + business_id + '/reviews'
    url = '{0}{1}'.format(API_HOST, quote(business_path.encode('utf8')))
    response = requests.get(url, headers=headers)
    reviews = response.json().get('reviews', [])

    for review in reviews:
        cursor.execute('''
            INSERT INTO reviews (id, restaurant_id, text, rating, time_created) 
            VALUES (?, ?, ?, ?, ?)
        ''', (review['id'], business_id, review['text'], review['rating'], review['time_created']))

    cursor.connection.commit()

    return reviews


def store_data():
    connection = sqlite3.connect("../data/raw/restaurants_data.db")
    cursor = connection.cursor()
    cursor.execute(query)
    cursor.execute(query_)

    business_ids = search_business_ids(cursor)
    for business_id in business_ids:
        reviews = get_reviews(business_id, cursor)
        if reviews:
            connection.commit()


store_data()

