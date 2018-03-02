'''
SQLite Twitter Stream Listener
Created on February 17, 2018

@author: Kevin Chuang

'''

import tweepy
from tweepy import Stream
import json
from credentials import *
import sqlite3

db = sqlite3.connect('Tweets.db')
db.executescript('''PRAGMA foreign_keys=on;''')
cursor = db.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS Tweets
                 (tweetID VARCHAR PRIMARY KEY, 
                 creationDate DATETIME NOT NULL, 
                 userName VARCHAR NOT NULL, 
                 tweetText VARCHAR NOT NULL,
                 coordinates VARCHAR,
                 userTimeZone VARCHAR,
                 userLocation VARCHAR,
                 retweeted VARCHAR)''')


def authenticate():
    ''' Uses credential.py file to authenticate user'''
    auth = tweepy.OAuthHandler(CONSUMER_KEY,CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
    api = tweepy.API(auth)
    return api, auth


# Override tweepy.StreamListener functions for needs
class SQLiteStreamListener(tweepy.StreamListener):

    def on_connect(self):
        """Called once connected to streaming server.
        This will be invoked once a successful response
        is received from the server. Allows the listener
        to perform some work prior to entering the read loop.
        """
        print 'Successful response received from Twitter streaming server! \n'

    def on_data(self, data):
        all_data = json.loads(data)
        # collect all desired data fields
        if 'text' in all_data:
            tweet_id = all_data["id_str"]
            tweet = all_data["text"]
            created_at = all_data["created_at"]
            retweeted = all_data["retweeted"]
            username = all_data["user"]["screen_name"]
            user_tz = all_data["user"]["time_zone"]
            user_location = all_data["user"]["location"]
            user_coordinates = all_data["coordinates"]

            # if coordinates are not present store blank value
            # otherwise get the coordinates.coordinates value
            if user_coordinates is None:
                final_coordinates = user_coordinates
            else:
                final_coordinates = str(all_data["coordinates"]["coordinates"])

            record = (tweet_id, created_at, username, tweet,
                      final_coordinates, user_tz, user_location, retweeted)
            # insert values into the db
            cursor.execute(
                "INSERT INTO Tweets(tweetID, creationDate, userName, tweetText, coordinates, "
                "userTimeZone, userLocation, retweeted) VALUES (?,?,?,?,?,?,?,?)",
                record)
            db.commit()

            print((username, tweet))

            return True
        else:
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


def main():
    api, auth = authenticate()

    stream = Stream(auth, SQLiteStreamListener())
    stream.filter(track=['#WomensHistoryMonth'])


if __name__ == '__main__':
    main()
