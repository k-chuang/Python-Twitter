import tweepy
from MyStreamListener import MyStreamListener
from tweepy import Stream
from credentials import *


def authenticate():
    ''' Uses credential.py file to authenticate user'''
    auth = tweepy.OAuthHandler(CONSUMER_KEY,CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
    api = tweepy.API(auth)
    return api, auth


def main():
    api, auth = authenticate()

    #Real-time streaming of data
    stream = Stream(auth, MyStreamListener())
    stream.filter(track=['#Olympics'], async=True)
    #stream.filter(follow=['user_id'], async=True)


if __name__ == '__main__':
    main()