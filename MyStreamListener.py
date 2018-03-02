'''
My Stream Listener
Created on February 17, 2018

@author: Kevin Chuang

'''

import tweepy
import json


# Override tweepy.StreamListener functions for needs
class MyStreamListener(tweepy.StreamListener):

    def on_connect(self):
        """Called once connected to streaming server.
        This will be invoked once a successful response
        is received from the server. Allows the listener
        to perform some work prior to entering the read loop.
        """
        print 'Successful response received from Twitter streaming server! \n'

    def on_status(self, status):
        # Prints the text of the tweet
        print('Tweet text: ' + status.text)
        post = status.text.replace('\n', ' ')
        print(str(status.created_at)
              + ', Author: '
              + status.user.name
              + ', Screen Name: '
              + status.user.screen_name
              + ', Tweet text: '
              + post)
        with open('stream_tweets.json','a') as fp:
            json.dump(status._json, fp, indent=4)
        return True

    def on_error(self, status_code):
        # HTTP Error Codes
        # Enhance the Calm Error and Too Many Requests Error
        if status_code == 420 or status_code == 429:
            # returning False in on_data disconnects the stream
            # status code 420 will increase wait time if we don't disconnect
            return False
        else:
            print('Error with status code: ' + str(status_code))
            return True  # To continue listening

    def on_timeout(self):
        print('Timeout...')
        return True  # To continue listening

    def on_friends(self, friends):
        """Called when a friends list arrives.
        friends is a list that contains user_id
        """
        print 'A friend recently tweeted about this!'
        return

    def on_warning(self, notice):
        """Called when a disconnection warning message arrives"""
        print 'Disconnection warning message has arrived...'
        return

    def on_limit(self, track):
        """Called when a limitation notice arrives"""
        print 'Limitation notice has arrived...'
        return

