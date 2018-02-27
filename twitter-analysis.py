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
    # Matches any tagged users, any regular alphanumeric expression, or website
    return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split())


def analyze_sentiment(tweet):
    '''
    Utility function to classify the polarity of a tweet
    using textblob.
    '''
    analysis = TextBlob(clean_tweet(tweet))
    if analysis.sentiment.polarity > 0:
        return 1
    elif analysis.sentiment.polarity == 0:
        return 0
    else:
        return -1


def main():
    api, auth = authenticate()

    ## Sentiment Analysis of tweets
    tweets = get_tweets_from_user(api,screen_name="realDonaldTrump")
    print("Number of tweets extracted: {}.\n".format(len(tweets)))

    # Create a pandas dataframe and add to it (Need to work on shortening this)
    data = pd.DataFrame(data=[tweet.text.encode("utf-8") for tweet in tweets], columns=['Tweets'])
    data['len'] = np.array([len(tweet.text) for tweet in tweets])
    data['ID'] = np.array([tweet.id for tweet in tweets])
    data['Date'] = np.array([tweet.created_at for tweet in tweets])
    data['Source'] = np.array([tweet.source for tweet in tweets])
    data['Likes'] = np.array([tweet.favorite_count for tweet in tweets])
    data['RTs'] = np.array([tweet.retweet_count for tweet in tweets])

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
    data['SA'] = np.array([analyze_sentiment(tweet) for tweet in data['Tweets']])

    # We construct lists with classified tweets:
    pos_tweets = [tweet for index, tweet in enumerate(data['Tweets']) if data['SA'][index] > 0]
    neu_tweets = [tweet for index, tweet in enumerate(data['Tweets']) if data['SA'][index] == 0]
    neg_tweets = [tweet for index, tweet in enumerate(data['Tweets']) if data['SA'][index] < 0]

    # Print percentages
    print("Percentage of positive tweets: {}%"
          .format(len(pos_tweets) * 100 / len(data['Tweets'])))
    print("Percentage of neutral tweets: {}%"
          .format(len(neu_tweets) * 100 / len(data['Tweets'])))
    print("Percentage de negative tweets: {}%"
          .format(len(neg_tweets) * 100 / len(data['Tweets'])))


if __name__ == '__main__':
    main()