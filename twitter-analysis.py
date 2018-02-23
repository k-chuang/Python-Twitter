#!/usr/bin/env python

import csv
import json
import re
import time
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import tweepy
from credentials import *
from textblob import TextBlob
from tweepy import Stream
from MyStreamListener import MyStreamListener
from pprint import pprint

def OAuthentication():
    ''' Uses credential.py file to authenticate user'''
    auth = tweepy.OAuthHandler(CONSUMER_KEY,CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
    api = tweepy.API(auth)
    return api, auth

def limit_handled(cursor):
    ''' Handles limits of Twitter API '''
    while True:
        try:
            yield cursor.next()
        except tweepy.RateLimitError:
            time.sleep(13 * 60)
            print '2 minutes remaining...'
            time.sleep(2 * 60)
        except tweepy.error.TweepError:
            time.sleep(13 * 60)
            print '2 minutes remaining...'
            time.sleep(2 * 60)

def write_json(tweets, filename):
    ''' Function that appends tweets to a file. '''
    json_obj = []
    with open(filename, 'w') as f:
        for tweet in tweets:
            json_obj.append(tweet._json)
        json.dump(json_obj, f, indent=4, sort_keys=True)

def print_limit_status(api):
    print json.dumps(api.rate_limit_status(), indent=4, sort_keys=True)

def get_tweets(api, query=None, item_num=100, favorite_count=0, retweet_count=0):
    ## Grabs unique tweets with specifications
    ## returns list of tweets with more information
    ids = set()
    t_list = []
    for tweet in limit_handled(tweepy.Cursor(
            api.search,
            q=query,
            lang="en", include_rts = False).items(item_num)):
        if (not tweet.retweeted) \
                and ('RT @' not in tweet.text) \
                and (int(tweet.favorite_count) >= favorite_count) \
                and (int(tweet.retweet_count) >= retweet_count):
            post = tweet.text
            post = post.replace('|', ' ')
            post = post.replace('\n', ' ')
            t_list.append([tweet.created_at, post.encode('utf-8'), tweet.favorite_count, tweet.retweet_count, tweet.id,
                 tweet.user.screen_name])
            ids.add(tweet.id)  # add new id
            print ("number of unique ids seen so far: {}".format(len(ids)))
    return t_list

def writeCSV(filename, tweet_list):
    ''' Write a list of tweets to a csv file'''
    try:
        tweet_list = iter(tweet_list)
    except TypeError, te:
        print tweet_list, 'is not iterable'
    csvFile = open(filename + '.csv', 'w')
    csvWriter = csv.writer(csvFile)
    for tweet in tweet_list:
        csvWriter.writerow(tweet)
    if csvFile.tell():
        csvFile.close()
        return 'Successfully added to CSV file!'
    else:
        csvFile.close()
        return 'Could not find any tweets with this query...'

def grab_trends(api, woeid=1):
    '''Grab trends based on woeid, default is woeid is WorldWide'''
    if hasattr(woeid, '__iter__'):
        trend_data_list = []
        for w in woeid:
            trends = api.trends_place(w)
            data = trends[0]
            location = data['locations'][0]['name']
            trends = data['trends']
            names = [trend['name'] for trend in trends]
            tweet_volume = ['Number of tweets: ' + str(trend['tweet_volume']) for trend in trends]
            url = [trend['url'] for trend in trends]
            trend_data = zip(names, tweet_volume, url)
            trend_data = {location: trend_data}
            trend_data_list.append(trend_data)
        return trend_data_list
    trends = api.trends_place(woeid)
    data = trends[0]
    location = data['locations'][0]['name']
    trends = data['trends']
    # grab the information from each trend (name, tweet volume, and url)
    names = [trend['name'] for trend in trends]
    tweet_volume = ['Number of tweets: ' + str(trend['tweet_volume']) for trend in trends]
    url = [trend['url'] for trend in trends]
    trend_data = zip(names,tweet_volume,url)
    trend_data = {location:trend_data}
    return trend_data

def get_woeid(api,locations):
    ## locations refer to a list of strings that represent a city/region/town recognized by Twitter
    trends_available = api.trends_available()
    list_of_places = filter(lambda l: l['name'] in locations, trends_available)
    ## If empty list/ string not recognized
    if not list_of_places:
        print 'Warning: the location you entered in was not recognized!'
        print 'Defaulting to WorldWide woeid of 1...'
        return 1
    elif len(list_of_places) > 1:
        woeid_list = []
        for places in list_of_places:
            woeid_list.append(places['woeid'])
        return woeid_list
    ## Use case for one location look up
    place = reduce(lambda k,v: k.update(v) or k, list_of_places, {})
    woeid = place['woeid']
    return woeid

def start_stream(auth, StreamListener):
    stream = Stream(auth, MyStreamListener())
    return stream

def clean_tweet(tweet):
    '''
    Utility function to clean the text in a tweet by removing
    links and special characters using regex.
    '''
    ## matches any tagged users, any regular alphanumeric expression, or website
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
    api, auth = OAuthentication()

    ## Gather tweets with a certain query
    #tweet_list = get_tweets(api,query='#Olympics')
    #write_status = writeCSV('OlympicTweets',tweet_list)
    #print write_status

    ## Trends
    #trends = grab_trends(api)
    #for t in trends:
    #    print t
    ## location can be a string with location information or a list of strings
    #location = ' '
    #trends = grab_trends(api, get_woeid(api,['San Jose','San Francisco']))
    #pprint(trends)

    ## Real-time streaming of data
    #stream = Stream(auth, MyStreamListener())
    #stream.filter(track=['#Olympics'], async=True)
    #stream.filter(follow=['user_id'], async=True)

    ## Sentiment Analysis of tweets
    tweets = api.user_timeline(screen_name="StephenAtHome", count=200)
    print("Number of tweets extracted: {}.\n".format(len(tweets)))

    # Create a pandas dataframe and add to it (Need to work on shortening this)
    data = pd.DataFrame(data=[tweet.text for tweet in tweets], columns=['Tweets'])
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
    pos_tweets = [tweet for index,
                            tweet in enumerate(data['Tweets']) if data['SA'][index] > 0]
    neu_tweets = [tweet for index,
                            tweet in enumerate(data['Tweets']) if data['SA'][index] == 0]
    neg_tweets = [tweet for index,
                            tweet in enumerate(data['Tweets']) if data['SA'][index] < 0]

    # Print percentages
    print("Percentage of positive tweets: {}%"
          .format(len(pos_tweets) * 100 / len(data['Tweets'])))
    print("Percentage of neutral tweets: {}%"
          .format(len(neu_tweets) * 100 / len(data['Tweets'])))
    print("Percentage de negative tweets: {}%"
          .format(len(neg_tweets) * 100 / len(data['Tweets'])))

if __name__ == '__main__':
    main()