#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import tweepy
import json
import os
import sys
import urllib.request
import yaml


parser = argparse.ArgumentParser()
parser.add_argument('--configuration', '-c', help="the path to the config folder", type=str)
parser.add_argument('--verbose', '-v', help="enable verbose logging", type=bool, default=False)

args = parser.parse_args()
if args.configuration == None:
    print(parser.format_help())
    raise FileNotFoundError("You haven't specified a configuration path")

yaml_conf = os.path.join(args.configuration, 'configuration.yml')

with open(yaml_conf, 'r') as f:
    conf = yaml.load(f)
    if args.verbose:
        print(yaml.dump(conf, default_flow_style=False))

settings = conf.get('general')
print('Grabbing all new tweets for user: {}'.format(settings['userid']))

media_path = os.path.join(settings.get('save_path'), 'media')
if not os.path.exists(media_path):
    print('path: {} does not exist, creating...'.format(media_path))
    os.mkdir(media_path)

db_file = os.path.join(settings.get('save_path'), 'db.json')

# Load credentials from json file
creds = conf.get('credentials')

consumer_key = creds['consumer_key']
consumer_secret = creds['consumer_secret']
access_token = creds['access_token']
access_token_secret = creds['access_secret']


# The number of tweets to get since the last collected ID.
max_tweets = 999

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth)

# Database file (JSON)
try:
    with open(db_file, 'r') as f:
        jdb = json.load(f)
except:
    raise FileNotFoundError("Database not found!")


allowed = [
    '_api', '_json', 'author', 'contributors', 'coordinates', 'created_at', 'destroy', 'display_text_range', 'entities',
    'extended_entities', 'favorite', 'favorite_count', 'favorited', 'full_text', 'geo', 'id', 'id_str',
    'in_reply_to_screen_name', 'in_reply_to_status_id', 'in_reply_to_status_id_str', 'in_reply_to_user_id',
    'in_reply_to_user_id_str', 'is_quote_status', 'lang', 'parse', 'parse_list', 'place', 'possibly_sensitive',
    'retweet', 'retweet_count', 'retweeted', 'retweets', 'source', 'source_url', 'truncated', 'user'
]

db_tweet_ids = sorted([tweet.get('tweet_id') for tweet in jdb.get('tweets')])

last_found_tweet = str(db_tweet_ids[-1])

print('getting primary feed...')
feed = api.user_timeline(id=settings['userid'],
                         since_id=last_found_tweet,
                         count=max_tweets,
                         tweet_mode='extended',
                         include_rts=False)

print('found', len(feed), 'tweets since tweet.id = {}'.format(last_found_tweet))

def get_media_metadata(filename, entity):
    """
    :param filename:
    :param entity:
    :return:
    """
    return {
        "media_id": str(entity.get('id')),
        "filename": filename,
        "media_url": entity.get('media_url')
    }

def parse_tweet(tweet):
    """

    :param tweet:
    :return:
    """
    media_list = []
    if 'extended_entities' in tweet._json.keys():
        if 'media' in tweet.extended_entities.keys():
            for i, media in enumerate(tweet.extended_entities['media']):
                file_type = media.get('media_url').split('.')[-1]
                filename = str(tweet.id) + '_' + str(i + 1) + '.' + file_type
                media_list.append(get_media_metadata(filename, media))
    elif 'media' in tweet.entities.keys():  # Get the simple media entries if else
        for i, media in enumerate(tweet.entities['media']):
            file_type = media.get('media_url').split('.')[-1]
            filename = str(tweet.id) + '_' + str(i + 1) + '.' + file_type
            media_list.append(get_media_metadata(filename, media))

    if settings['download_media']:
        for media in media_list:
            urllib.request.urlretrieve(media.get('media_url'), media_path + media.get('filename'))

    thistweet = {
        "tweet_id": tweet.id,
        "created_at": str(tweet.created_at),
        "author": tweet.user.screen_name,
        "in_reply_to": tweet.in_reply_to_screen_name,
        "in_reply_to_status_id": tweet.in_reply_to_status_id,
        "text": tweet._json['full_text'],
        "media": media_list
    }

    return thistweet

new_tweets = []
reply_ids = []
parsed_ids = []
for tweet in feed:
    new_tweets.append(parse_tweet(tweet))
    reply_ids.append(tweet.in_reply_to_status_id)
    parsed_ids.append(tweet.id)

# Get a list of the parent tweets not already grabbed
parent_ids = [id for id in reply_ids if id not in parsed_ids]

print('getting originals from replies...')
feed = api.statuses_lookup(parent_ids, tweet_mode='extended')

print('found', len(feed), 'unique tweets upstream of replies from primary user')
for tweet in feed:
    new_tweets.append(parse_tweet(tweet))

sorted_tweets = sorted(new_tweets, key=lambda x: x['tweet_id'], reverse=True)

jdb['tweets'] = sorted_tweets + jdb['tweets']

print('saving to database...')
with open(db_file, 'w') as f:
    json.dump(jdb, f)

print('database now stands at {} captured tweets'.format(len(jdb['tweets'])))
