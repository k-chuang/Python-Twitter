import tweepy
import time
import csv
from credentials import *


def authenticate():
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


def search_unique_tweets(api, query=None, item_num=100, favorite_count=0, retweet_count=0):
    # Grabs unique/non-retweeted tweets with specifications
    # Returns list of tweets with more information
    ids = set()
    t_list = []
    for tweet in limit_handled(tweepy.Cursor(
            api.search,
            q=query,
            lang="en").items(item_num)):
        if (not tweet.retweeted) \
                and ('RT @' not in tweet.text) \
                and (int(tweet.favorite_count) >= favorite_count) \
                and (int(tweet.retweet_count) >= retweet_count):
            post = tweet.text
            post = post.replace('|', ' ')
            post = post.replace('\n', ' ')
            #t_list.append([tweet.created_at,
            #               post.encode('utf-8'),
            #               tweet.favorite_count,
            #               tweet.retweet_count,
            #               tweet.id,
            #               tweet.user.screen_name])
            t_list.append(tweet)
            ids.add(tweet.id)
            print ("number of unique ids seen so far: {}".format(len(ids)))
    return t_list


def get_tweets_from_user(api, screen_name, all_tweets=[], max_id=0):
    # Twitter only allows access to a users most recent 3240 tweets with this method
    # Make initial request for most recent tweets (200 is the maximum allowed count)
    if max_id is 0:
        new_tweets = api.user_timeline(screen_name=screen_name, count=200)
    else:
        new_tweets = api.user_timeline(screen_name=screen_name, count= 200, max_id=max_id)

    if len(new_tweets) > 0:
        all_tweets.extend(new_tweets)
        oldest_tweet = all_tweets[-1]
        oldest_id = oldest_tweet.id - 1
        oldest_date = oldest_tweet.created_at
        print " Getting tweets before %s" % (str(oldest_date))
        print "...%s tweets extracted so far" % (len(all_tweets))
        return get_tweets_from_user(api, screen_name=screen_name, all_tweets=all_tweets, max_id=oldest_id)

    #out_tweets = [[tweet.id_str, tweet.created_at, tweet.text.encode("utf-8")] for tweet in all_tweets]

    return all_tweets


def write_csv(filename, tweet_list):
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
        return 'Failed to write CSV file...'


def main():

    api, auth = authenticate()

    # Gather tweets with a certain query
    query = '#ThingsPeopleShouldKnow'
    tweet_list = search_unique_tweets(api, query=query)
    write_status = write_csv(query, tweet_list)
    print write_status

    # Grab all possibly allowed tweets (3240 tweets) from a particular user
    screen_name = 'realDonaldTrump'
    all_tweets = get_tweets_from_user(api, screen_name, [], 0)
    status = write_csv('%s_tweets' % screen_name, all_tweets)
    print status


if __name__ == '__main__':
    main()