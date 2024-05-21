import sqlite3
import requests
from urllib.parse import quote

# run this file to obtain the review data that was not collected due to Yelp's daily limit on API calls.
API_KEY = 'JStjU0QvRKGR6QbifP-Hj063lBU0Gf3cMeUuOsdVcQsLBqzhvRl-6d7jINUHjBo5TmRdJGLFrH2vFKb5P9QULxdPKxCCKzGDdZBkUhHWlETiN5D32qZ7wPpeGBFbZXYx'
API_HOST = 'https://api.yelp.com'
BUSINESS_PATH = '/v3/businesses/'
headers = {'Authorization': 'Bearer %s' % API_KEY}


def get_reviews(business_id, cursor):
    business_path = BUSINESS_PATH + business_id + '/reviews'
    url = '{0}{1}'.format(API_HOST, quote(business_path.encode('utf8')))
    response = requests.get(url, headers=headers)
    reviews = response.json().get('reviews', [])

    for review in reviews:
        cursor.execute('''
            INSERT OR IGNORE INTO reviews (id, restaurant_id, text, rating, time_created) 
            VALUES (?, ?, ?, ?, ?)
        ''', (review['id'], business_id, review['text'], review['rating'], review['time_created']))

    cursor.connection.commit()
    return reviews


def get_missing_reviews():
    connection = sqlite3.connect('../data/raw/restaurants_data.db')
    cursor = connection.cursor()

    cursor.execute('SELECT id FROM restaurants')
    restaurant_ids = [row[0] for row in cursor.fetchall()]

    cursor.execute('SELECT DISTINCT restaurant_id FROM reviews')
    reviewed_restaurants = set(row[0] for row in cursor.fetchall())
    missing_reviews_restaurants = [id for id in restaurant_ids if id not in reviewed_restaurants]

    for business_id in missing_reviews_restaurants:
        reviews = get_reviews(business_id, cursor)
        if reviews:
            print(f'Collected reviews for restaurant ID: {business_id}')

    connection.close()


get_missing_reviews()
