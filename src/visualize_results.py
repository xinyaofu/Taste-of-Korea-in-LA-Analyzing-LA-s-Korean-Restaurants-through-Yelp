import sqlite3
import pandas as pd
from nltk.corpus import stopwords
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import folium
from folium.plugins import MarkerCluster
import numpy as np


connection = sqlite3.connect('../data/processed/data_analysis.db')
analysis_restaurants = pd.read_sql_query('SELECT * FROM restaurants', connection)
analysis_reviews = pd.read_sql_query('SELECT * FROM reviews', connection)
df_top_10_words_high_rating = pd.read_sql_query('SELECT * FROM top_10_words_high_rating', connection)
df_top_10_words_low_rating = pd.read_sql_query('SELECT * FROM top_10_words_low_rating', connection)
df_top_10_service_high_rating = pd.read_sql_query('SELECT * FROM top_10_words_service_high_rating', connection)
df_top_10_service_low_rating = pd.read_sql_query('SELECT * FROM top_10_words_service_low_rating', connection)
df_top_10_trigrams_high_rating = pd.read_sql_query('SELECT * FROM top_10_trigrams_high_rating', connection)
df_top_10_trigrams_low_rating = pd.read_sql_query('SELECT * FROM top_10_trigrams_low_rating', connection)
connection.close()

stop_words = set(stopwords.words('english'))
stop_words.update(['place', 'one', 'get', 'got', "I've", "I'm", 'came'])

# text analysis
# word cloud for all reviews
cloud_text = ' '.join(analysis_reviews['translated_text'])
text_no_stopword = WordCloud(background_color='white', stopwords=stop_words).generate(cloud_text)
plt.imshow(text_no_stopword, interpolation='bilinear')
plt.axis('off')
plt.show()

# word cloud for reviews with a sentiment analysis score equal or greater than 0
positive_reviews = analysis_reviews[analysis_reviews['sentiment_score'] >= 0]
positive_text = ' '.join(positive_reviews['translated_text'])

text_no_stopword = WordCloud(background_color='white', stopwords=stop_words).generate(positive_text)
plt.imshow(text_no_stopword, interpolation='bilinear')
plt.axis('off')
plt.show()

# word cloud for reviews with a sentiment analysis score less thank 0
negative_reviews = analysis_reviews[analysis_reviews['sentiment_score'] < 0]
negative_text = ' '.join(negative_reviews['translated_text'])

text_no_stopword = WordCloud(background_color='white', stopwords=stop_words).generate(negative_text)
plt.imshow(text_no_stopword, interpolation='bilinear')
plt.axis('off')
plt.show()

# word cloud for reviews with a rating greater than 2
high_reviews_rating = analysis_reviews[analysis_reviews['rating'] > 2]
high_text_rating = ' '.join(high_reviews_rating['translated_text'])

text_no_stopword = WordCloud(background_color='white', stopwords=stop_words).generate(high_text_rating)
plt.imshow(text_no_stopword, interpolation='bilinear')
plt.axis('off')
plt.show()

# word cloud for reviews with a rating less than or equal to 2
low_reviews_rating = analysis_reviews[analysis_reviews['rating'] <= 2]
low_text_rating = ' '.join(low_reviews_rating['translated_text'])

text_no_stopword = WordCloud(background_color='white', stopwords=stop_words).generate(low_text_rating)
plt.imshow(text_no_stopword, interpolation='bilinear')
plt.axis('off')
plt.show()


def create_horizontal_bar_chart(dataframe, y_column, x_column, chart_title):
    labels = dataframe[y_column]
    values = dataframe[x_column]
    y_pos = np.arange(len(labels))
    fig, ax = plt.subplots(figsize=(30, 8))
    ax.barh(y_pos, values, align='center')
    ax.set_title(chart_title, fontsize=20)
    ax.set_yticks(y_pos)
    ax.invert_yaxis()
    ax.set_yticklabels(labels, fontsize=20, rotation=45)
    ax.set_xlabel('Frequency', fontsize=18)
    plt.show()


create_horizontal_bar_chart(df_top_10_words_high_rating, 'Word', 'Frequency', 'Top 10 Words - High Rating')
create_horizontal_bar_chart(df_top_10_words_low_rating, 'Word', 'Frequency', 'Top 10 Words - Low Rating')
create_horizontal_bar_chart(df_top_10_service_high_rating, 'Word', 'Frequency', 'Top 10 Words Around Service - High Rating')
create_horizontal_bar_chart(df_top_10_service_low_rating, 'Word', 'Frequency', 'Top 10 Words Around Service - Low Rating')
create_horizontal_bar_chart(df_top_10_trigrams_high_rating, 'Trigram', 'Frequency', 'Top 10 Trigrams - High Rating')
create_horizontal_bar_chart(df_top_10_trigrams_low_rating, 'Trigram', 'Frequency', 'Top 10 Trigrams - Low Rating')

# visualization of restaurants' locations using Folium
la_k_restaurant_map = folium.Map(location=[34.0522, -118.2437], zoom_start=10)

marker_cluster = MarkerCluster().add_to(la_k_restaurant_map)

for idx, row in analysis_restaurants.iterrows():
    folium.Marker(
        [row['latitude'], row['longitude']],
        popup=f'Rating: {row["rating"]} \n#Reviews: {row["review_count"]}'
    ).add_to(marker_cluster)

la_k_restaurant_map.save('la_k_restaurant_map.html')
