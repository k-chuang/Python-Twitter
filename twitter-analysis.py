#!/usr/bin/env python

import csv
import json
import re
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import tweepy
from credentials import *
from textblob import TextBlob
from grab_trends import grab_trends, get_woeid
from search_tweets import get_tweets_from_user, search_unique_tweets


def authenticate():
    ''' Uses credential.py file to authenticate user'''
    auth = tweepy.OAuthHandler(CONSUMER_KEY,CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
    api = tweepy.API(auth)
    return api, auth


def write_json(tweets, filename):
    ''' Function that appends tweets to a file. '''
    json_obj = []
    with open(filename, 'w') as f:
        for tweet in tweets:
            json_obj.append(tweet._json)
        json.dump(json_obj, f, indent=4, sort_keys=True)


def clean_tweet(tweet):
    '''
    Utility function to clean the text in a tweet by removing
    links and special characters using regex.
    '''
    # Removes any tagged users, any regular alphanumeric expression, or website
    return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split())


def analyze_sentiment(tweet):
    '''
    Utility function to classify the polarity of a tweet
    using textblob.
    '''
    tweet = clean_tweet(tweet)
    analysis = TextBlob(tweet)
    if analysis.sentiment.polarity > 0:
        return 1
    elif analysis.sentiment.polarity == 0:
        return 0
    else:
        return -1

def analyze_raw_sentiment(tweet):
    tweet = clean_tweet(tweet)
    analysis = TextBlob(tweet)
    return analysis.sentiment.polarity


def analyze_subjectivity(tweet):
    '''
    Utility function to classify subjectivity of tweet
    0 is very objective, 1 is very subjective
    :param tweet:
    :return:
    '''
    tweet = clean_tweet(tweet)
    analysis = TextBlob(tweet)
    if analysis.sentiment.subjectivity >= 0.5:
        return 1
    else:
        return 0


def make_autopct(values):
    def my_autopct(pct):
        total = sum(values)
        val = int(round(pct*total/100.0))
        return '{p:.2f}%  ({v:d})'.format(p=pct,v=val)
    return my_autopct


def main():
    api, auth = authenticate()

    # Sentiment Analysis of tweets
    query = '#SamsungGalaxyS9'
    tweets = search_unique_tweets(api, query=query, item_num=1000)
    # tweets = get_tweets_from_user(api,screen_name="realDonaldTrump")
    print("Number of tweets extracted: {}.\n".format(len(tweets)))

    # Create a pandas dataframe and add to it (Need to work on shortening this)
    data = pd.DataFrame(data=[tweet.text.encode("utf-8") for tweet in tweets], columns=['Tweets'])
    data['len'] = np.array([len(tweet.text) for tweet in tweets])
    data['ID'] = np.array([tweet.id for tweet in tweets])
    data['Date'] = np.array([tweet.created_at for tweet in tweets])
    data['Source'] = np.array([tweet.source for tweet in tweets])
    data['Likes'] = np.array([tweet.favorite_count for tweet in tweets])
    data['RTs'] = np.array([tweet.retweet_count for tweet in tweets])
    data['User Location'] = np.array([tweet.user.location for tweet in tweets])
    # data['Coordinates'] = np.array([tweet.coordinates.coordinates for tweet in tweets])
    # data['Country'] = np.array([tweet.place.country for tweet in tweets])
    # data['City'] = np.array([tweet.place.name for tweet in tweets])
    # data['Type of Place'] = np.array([tweet.place.place_type for tweet in tweets])

    fav_max = np.max(data['Likes'])
    rt_max = np.max(data['RTs'])
    fav = data[data.Likes == fav_max].index[0]
    rt = data[data.RTs == rt_max].index[0]

    # Max FAVs:
    print("The tweet with more likes is: \n{}".format(data['Tweets'][fav]))
    print("Number of likes: {}".format(fav_max))
    print("{} characters.\n".format(data['len'][fav]))

    # Max RTs:
    print("The tweet with more retweets is: \n{}".format(data['Tweets'][rt]))
    print("Number of retweets: {}".format(rt_max))
    print("{} characters.\n".format(data['len'][rt]))

    # We create time series for data:
    tlen = pd.Series(data=data['len'].values, index=data['Date'])
    tfav = pd.Series(data=data['Likes'].values, index=data['Date'])
    tret = pd.Series(data=data['RTs'].values, index=data['Date'])

    # Lengths along time:
    tlen.plot(figsize=(16, 4), color='r')
    plt.show()

    # Likes vs retweets visualization:
    tfav.plot(figsize=(16, 4), label="Likes", legend=True)
    tret.plot(figsize=(16, 4), label="Retweets", legend=True)
    plt.show()

    # Obtain all the unique sources of user's tweets
    sources = data['Source'].unique()
    sources = [source.encode("utf-8") for source in sources]

    # Print source list to get visual idea
    print("Creation of content sources:")
    for source in sources:
        print("* {}".format(source))

    num_of_values = data['Source'].count()
    df = data.groupby('Source').Tweets.nunique().reset_index(name='counts')
    df['Percent'] = (df['counts']/num_of_values) * 100

    # Visualizing percentages of sources via a pie chart
    pie_chart = pd.Series(df['Percent'].values, index=df['Source'].values, name='Sources')
    pie_chart.plot.pie(fontsize=11, autopct='%.2f', figsize=(6, 6))
    plt.show()

    # Create a column with the result of the analysis:
    data['Sentiment'] = np.array([analyze_sentiment(tweet) for tweet in data['Tweets']])
    data['Raw Sentiment'] = np.array([analyze_raw_sentiment(tweet) for tweet in data['Tweets']])
    data['Subjectivity'] = np.array([analyze_subjectivity(tweet) for tweet in data['Tweets']])

    # We construct lists with classified tweets:
    pos_tweets = [tweet for index, tweet in enumerate(data['Tweets']) if data['Sentiment'][index] > 0]
    neu_tweets = [tweet for index, tweet in enumerate(data['Tweets']) if data['Sentiment'][index] == 0]
    neg_tweets = [tweet for index, tweet in enumerate(data['Tweets']) if data['Sentiment'][index] < 0]

    obj_tweets = [tweet for index, tweet in enumerate(data['Tweets']) if data['Subjectivity'][index] == 0]
    subj_tweets = [tweet for index, tweet in enumerate(data['Tweets']) if data['Subjectivity'][index] == 1]

    # Print percentages
    print("Percentage of positive tweets: {}%"
          .format(len(pos_tweets) * 100 / len(data['Tweets'])))
    print("Percentage of neutral tweets: {}%"
          .format(len(neu_tweets) * 100 / len(data['Tweets'])))
    print("Percentage de negative tweets: {}%"
          .format(len(neg_tweets) * 100 / len(data['Tweets'])))

    num_of_values = len(data['Tweets'])
    df = data.groupby('Sentiment')['Tweets'].nunique().reset_index(name='counts')
    df['Sentiment Percent'] = (df['counts']/num_of_values) * 100
    df['Sentiment'] = df['Sentiment'].map({0: 'Neutral', 1: 'Positive', -1: 'Negative'})
    pie_chart = pd.Series(df['Sentiment Percent'].values,
                          index=df['Sentiment'].values,
                          name='')

    pie_chart.plot.pie(fontsize=11,
                       autopct=make_autopct(df['counts'].values),
                       figsize=(6, 6))
    plt.title('Sentiment Analysis for %s' % query)
    plt.show()

    raw_sent_over_time = pd.Series(data=data['Raw Sentiment'].values, index=data['Date'])

    # Raw sentiment over time:
    raw_sent_over_time.plot(figsize=(16, 4), color='r')
    plt.show()

    print("Percentage of objective tweets: {}%"
          .format(len(obj_tweets) * 100 / len(data['Tweets'])))
    print("Percentage de subjective tweets: {}%"
          .format(len(subj_tweets) * 100 / len(data['Tweets'])))


if __name__ == '__main__':
    main()