import sqlite3
import pandas as pd
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk.corpus import stopwords
from scipy import stats
from collections import Counter
import re
# import gensim
from gensim.models import Word2Vec
from nltk.tokenize import word_tokenize
from nltk.util import ngrams
import nltk
nltk.download('punkt', quiet=True)
nltk.download('vader_lexicon')
nltk.download('stopwords')

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

connection = sqlite3.connect('../data/processed/cleaned_data.db')
restaurants = pd.read_sql_query('SELECT * FROM restaurants', connection)
reviews = pd.read_sql_query('SELECT * FROM reviews', connection)
connection.close()

# sentiment analysis ---------------------------------------------------------------------------------------------------
sid = SentimentIntensityAnalyzer()
reviews['sentiment_score'] = reviews['translated_text'].apply(lambda text: sid.polarity_scores(text)['compound'])

new_connection = sqlite3.connect('../data/processed/data_analysis.db')
restaurants.to_sql('restaurants', new_connection, if_exists='replace', index=False)
reviews.to_sql('reviews', new_connection, if_exists='replace', index=False)

new_connection.close()

analysis_connection = sqlite3.connect('../data/processed/data_analysis.db')
analysis_restaurants = pd.read_sql_query('SELECT * FROM restaurants', analysis_connection)
analysis_reviews = pd.read_sql_query('SELECT * FROM reviews', analysis_connection)

# Outliers Analysis ----------------------------------------------------------------------------------------------------
analysis_reviews['adjusted_sentiment_score'] = 2.5 * (analysis_reviews['sentiment_score'] + 1) + 1
analysis_reviews['rating_diff'] = analysis_reviews['rating'] - analysis_reviews['adjusted_sentiment_score']
threshold = 3

outliers = analysis_reviews[abs(analysis_reviews['rating_diff']) > threshold]
print("\nNumber of outliers:", len(outliers))

# text analysis starts here --------------------------------------------------------------------------------------------
stop_words = set(stopwords.words('english'))
stop_words.update(['place', 'one', 'get', 'got', "I've", "I'm", 'came', 'super', 'know'])

# top 10 words in high rating reviews with their frequencies
high_reviews_rating = analysis_reviews[analysis_reviews['rating'] > 2]
high_text_rating = ' '.join(high_reviews_rating['translated_text'])

words = re.findall(r'\w+', high_text_rating.lower())
filtered_words = [word for word in words if word not in stop_words]
word_counts = Counter(filtered_words)
top_10_words_high_rating = word_counts.most_common(10)
print('\ntop 10 words in high rating reviews: \n', top_10_words_high_rating)

# top 10 words in low rating reviews with their frequencies
low_reviews_rating = analysis_reviews[analysis_reviews['rating'] <= 2]
low_text_rating = ' '.join(low_reviews_rating['translated_text'])

words = re.findall(r'\w+', low_text_rating.lower())
filtered_words = [word for word in words if word not in stop_words]
word_counts = Counter(filtered_words)
top_10_words_low_rating = word_counts.most_common(10)
print('\ntop 10 words in low rating reviews: \n', top_10_words_low_rating)


# Analyze the top 10 possible words around the word "service" using Word2Vec
def preprocess_text(text):
    text = text.lower()
    text = re.sub(r'[^a-z]', ' ', text)
    words = word_tokenize(text)
    words = [word for word in words if word not in stop_words]
    return words


# high rating reviews
processed_reviews_high_rating = [preprocess_text(review) for review in high_reviews_rating['translated_text']]
model = Word2Vec(sentences=processed_reviews_high_rating, vector_size=500, window=10, min_count=1, workers=4, sg=0)
possible_words_high_rating = model.wv.most_similar('service', topn=10)
print('\nTop 10 possible words around the word "service" for high rating reviews: \n', possible_words_high_rating)

# low rating reviews
processed_reviews_low_rating = [preprocess_text(review) for review in low_reviews_rating['translated_text']]
model = Word2Vec(sentences=processed_reviews_low_rating, vector_size=500, window=10, min_count=1, workers=4, sg=0)
possible_words_low_rating = model.wv.most_similar('service', topn=10)
print('\nTop 10 possible words around the word "service" for low rating reviews: \n', possible_words_low_rating)

# find the top 10 trigrams in reviews with a rating greater or equal to 3 using ngrams
processed_reviews_trigrams_high = [preprocess_text(review) for review in high_reviews_rating['translated_text']]
trigrams = [gram for review in processed_reviews_trigrams_high for gram in ngrams(review, 3)]
trigram_counts_high_rating = Counter(trigrams)
top_10_trigrams_high_rating = trigram_counts_high_rating.most_common(10)
print('\nTop 10 trigrams in high rating reviews: \n', top_10_trigrams_high_rating)

low_sentiment_score = analysis_reviews[analysis_reviews['sentiment_score'] < 0]

# find the top 10 trigrams in reviews with a rating lower than 3 using ngrams
processed_reviews_trigrams_low = [preprocess_text(review) for review in low_reviews_rating['translated_text']]
trigrams = [gram for review in processed_reviews_trigrams_low for gram in ngrams(review, 3)]
trigram_counts_low_rating = Counter(trigrams)
top_10_trigrams_low_rating = trigram_counts_low_rating.most_common(10)
print('\nTop 10 trigrams in low rating reviews: \n', top_10_trigrams_low_rating)

# price analysis starts here -------------------------------------------------------------------------------------------
analysis_restaurants.rename(columns={'rating': 'restaurant_rating'}, inplace=True)
analysis_reviews.rename(columns={'rating': 'review_rating'}, inplace=True)

merged_data = pd.merge(analysis_restaurants, analysis_reviews, left_on='id', right_on='restaurant_id', how='inner')

price_mapping = {'$': 1, '$$': 2, '$$$': 3, '$$$$': 4, 'unknown': None}
merged_data['price_level'] = merged_data['price'].map(price_mapping)

# mean and standard deviations of sentiment scores and review ratings based on price levels
grouped_stats = merged_data.groupby('price_level').agg({'sentiment_score': ['mean', 'std'], 'review_rating': ['mean', 'std']}).round(3)
print('\nMean and Standard Deviation:\n', grouped_stats)

# pearson correlation between price level, sentiment score, review rating and restaurant rating
pearson_correlation = merged_data[['price_level', 'sentiment_score', 'review_rating', 'restaurant_rating']].corr(method='pearson').round(3)
print('\nPearson Correlation:\n', pearson_correlation)

# spearman correlation between price level, sentiment score, review rating and restaurant rating
spearman_correlation = merged_data[['price_level', 'sentiment_score', 'review_rating', 'restaurant_rating']].corr(method='spearman').round(3)
print('\nSpearman Correlation:\n', spearman_correlation, '\n')

# t-test
columns_of_interest = ['price_level', 'sentiment_score', 'review_rating', 'restaurant_rating']
for i in range(len(columns_of_interest)):
    for j in range(i + 1, len(columns_of_interest)):
        col1 = columns_of_interest[i]
        col2 = columns_of_interest[j]
        temp_data = merged_data[[col1, col2]].dropna()
        corr, p_value = stats.pearsonr(temp_data[col1], temp_data[col2])
        print(f'Correlation between {col1} and {col2}: Pearson corr = {corr:.3f}, P-value = {p_value:.3f}')

# Store analysis results to SQLite database ----------------------------------------------------------------------------
df_top_10_words_high_rating = pd.DataFrame(top_10_words_high_rating, columns=['Word', 'Frequency'])
df_top_10_words_low_rating = pd.DataFrame(top_10_words_low_rating, columns=['Word', 'Frequency'])
df_top_10_service_high_rating = pd.DataFrame(possible_words_high_rating, columns=['Word', 'Frequency'])
df_top_10_service_low_rating = pd.DataFrame(possible_words_low_rating, columns=['Word', 'Frequency'])
df_top_10_trigrams_high_rating = pd.DataFrame(top_10_trigrams_high_rating, columns=['Trigram', 'Frequency'])
df_top_10_trigrams_low_rating = pd.DataFrame(top_10_trigrams_low_rating, columns=['Trigram', 'Frequency'])

df_top_10_trigrams_high_rating['Trigram'] = df_top_10_trigrams_high_rating['Trigram'].apply(lambda x: ' '.join(x))
df_top_10_trigrams_low_rating['Trigram'] = df_top_10_trigrams_low_rating['Trigram'].apply(lambda x: ' '.join(x))

df_top_10_words_high_rating.to_sql('top_10_words_high_rating', analysis_connection, if_exists='replace', index=False)
df_top_10_words_low_rating.to_sql('top_10_words_low_rating', analysis_connection, if_exists='replace', index=False)
df_top_10_service_high_rating.to_sql('top_10_words_service_high_rating', analysis_connection, if_exists='replace', index=False)
df_top_10_service_low_rating.to_sql('top_10_words_service_low_rating', analysis_connection, if_exists='replace', index=False)
df_top_10_trigrams_high_rating.to_sql('top_10_trigrams_high_rating', analysis_connection, if_exists='replace', index=False)
df_top_10_trigrams_low_rating.to_sql('top_10_trigrams_low_rating', analysis_connection, if_exists='replace', index=False)

analysis_connection.close()
