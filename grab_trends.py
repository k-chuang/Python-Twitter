import tweepy
from pprint import pprint
from credentials import *


def authenticate():
    ''' Uses credential.py file and OAuth to authenticate user'''
    auth = tweepy.OAuthHandler(CONSUMER_KEY,CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
    api = tweepy.API(auth)
    return api, auth


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
    trend_data = zip(names, tweet_volume, url)
    trend_data = {location: trend_data}
    return trend_data


def get_woeid(api, locations):
    # locations refer to a list of strings that represent a city/region/town recognized by Twitter
    trends_available = api.trends_available()
    list_of_places = filter(lambda l: l['name'] in locations, trends_available)
    # If empty list/ string not recognized
    if not list_of_places:
        print 'Warning: the location you entered in was not recognized!'
        print 'Defaulting to WorldWide woeid of 1...'
        return 1
    elif len(list_of_places) > 1:
        woeid_list = []
        for places in list_of_places:
            woeid_list.append(places['woeid'])
        return woeid_list
    # Use case for one location look up
    place = reduce(lambda k, v: k.update(v) or k, list_of_places, {})
    woeid = place['woeid']
    return woeid


def main():

    api, auth = authenticate()

    # location can be a single string with location information or a list of strings
    location = ['San Jose', 'San Francisco']
    trends = grab_trends(api, get_woeid(api, location))
    pprint(trends)


if __name__ == '__main__':
    main()