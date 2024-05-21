import sqlite3
import pandas as pd
import numpy as np
from langdetect import detect
from deep_translator import GoogleTranslator
from spellchecker import SpellChecker
import re


connection = sqlite3.connect('../data/raw/restaurants_data.db')
restaurants = pd.read_sql_query('SELECT * FROM restaurants', connection)
reviews = pd.read_sql_query('SELECT * FROM reviews', connection)

# check if all the columns that are supposed to be integers or floats are numbers.
reviews['rating'] = pd.to_numeric(reviews['rating'], errors='coerce')
restaurants['rating'] = pd.to_numeric(restaurants['rating'], errors='coerce')
restaurants['review_count'] = pd.to_numeric(restaurants['review_count'], downcast='integer', errors='coerce')
restaurants['latitude'] = pd.to_numeric(restaurants['latitude'], errors='coerce')
restaurants['longitude'] = pd.to_numeric(restaurants['longitude'], errors='coerce')

restaurants['price'].replace('', np.nan, inplace=True)
restaurants['location'].replace('', np.nan, inplace=True)
restaurants.fillna('unknown', inplace=True)

# check the types of the data
print("Reviews data types：")
print(reviews.dtypes)
print("\nRestaurants data types：")
print(restaurants.dtypes)

# check if there's any NaN values in the database
print("\nReviews NaN values：")
print(reviews.isna().sum())
print("\nRestaurants NaN values：")
print(restaurants.isna().sum())

# check how many reviews are non-English
not_english_data = []
not_english_count = 0
for row in reviews['text']:
	if detect(row) != 'en':
		not_english_data.append(row)
		not_english_count += 1

print(not_english_data)
print(not_english_count)


# translate the non_English reviews to English
def translate_text(text):
	if detect(text) != 'en':
		return GoogleTranslator(source='auto', target='en').translate(text)
	else:
		return text


reviews['translated_text'] = reviews['text'].apply(translate_text)

spell_check = SpellChecker()


# correct the misspelling words in the reviews.
def correct_misspelling(text):
	words = re.findall(r'\b\w+\b|[^\w\s]', text)
	corrected_words = []

	for i, word in enumerate(words):
		if re.match(r'\b\w+\b', word):
			corrected_word = spell_check.correction(word)
			corrected_word = corrected_word if corrected_word is not None else word
		else:
			corrected_word = word
		corrected_words.append(corrected_word)
		if i < len(words) - 1 and re.match(r'\b\w+\b', words[i + 1]):
			corrected_words.append(' ')

	return ''.join(corrected_words)


reviews['corrected_text'] = reviews['translated_text'].apply(correct_misspelling)

new_conn = sqlite3.connect('../data/processed/cleaned_data.db')
restaurants.to_sql('restaurants', new_conn, index=False, if_exists='replace')
reviews.to_sql('reviews', new_conn, index=False, if_exists='replace')

new_conn.close()
connection.close()
