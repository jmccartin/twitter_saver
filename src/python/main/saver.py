#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import json
import logging
import os
import sys
import twitter
import yaml

from src.python.main.objects import MediaItem, Tweet

logging.basicConfig(level=logging.INFO)


def parse_tweet(tweet: twitter.Status) -> Tweet:
    """
    Converts each tweet (Status object from python-twitter)
    into a simplified format, while grabbing all media items
    on the fly.
    :param tweet: twitter.models.Status object
    :return: Tweet object
    """

    media_list = []

    if settings['download_media'] and tweet.media is not None:
        for media in tweet.media:
            media_obj = MediaItem(id=media.id,
                                  filename=media.media_url.split('/')[-1],
                                  url=media.media_url,
                                  type=media.type)
            media_obj.get_media(media_path)
            media_list.append(media_obj)

    print("parse tweet, tweet_id = {}".format(tweet.id))

    return Tweet(id=tweet.id,
                 created_at=str(tweet.created_at),
                 author=tweet.user.screen_name,
                 in_reply_to=tweet.in_reply_to_screen_name,
                 in_reply_to_status_id=tweet.in_reply_to_status_id,
                 text=tweet.text,
                 media=media_list)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--configuration', '-c', help="the path to the config folder", type=str)
    parser.add_argument('--verbose', '-v', help="enable verbose logging", type=bool, default=False)

    args = parser.parse_args()
    if args.configuration is None:
        logging.warning(parser.format_help())
        raise FileNotFoundError("You haven't specified a configuration path")

    yaml_conf = os.path.join(args.configuration, 'configuration.yml')

    with open(yaml_conf, 'r') as f:
        conf = yaml.load(f)
        if args.verbose:
            print(yaml.dump(conf, default_flow_style=False))

    settings = conf.get('general')
    user_id = settings['user_id']
    max_tweets = settings['max_tweets']
    save_path = os.path.join(settings.get('save_path'), user_id)

    logging.info('Grabbing all new tweets for user: {}'.format(user_id))

    media_path = os.path.join(save_path, 'media')
    if not os.path.exists(media_path):
        logging.info('path: {} does not exist, creating...'.format(media_path))
        os.makedirs(media_path)

    db_file = os.path.join(save_path, 'db-{}.json'.format(user_id))

    # Load credentials from json file
    credentials = conf.get('credentials')

    consumer_key = credentials['consumer_key']
    consumer_secret = credentials['consumer_secret']
    access_token = credentials['access_token']
    access_token_secret = credentials['access_secret']

    api = twitter.Api(consumer_key=consumer_key,
                      consumer_secret=consumer_secret,
                      access_token_key=access_token,
                      access_token_secret=access_token_secret)

    # Database file (JSON)
    try:
        with open(db_file, 'r') as f:
            jdb = json.load(f)
            # Sort the database to get the last known tweet
            db_tweet_ids = sorted([tweet.get('id') for tweet in jdb.get('tweets')])
            last_found_tweet = str(db_tweet_ids[-1])
    except FileNotFoundError:
        logging.warning("Database not found, creating new file...")
        jdb = {"tweets": []}
        last_found_tweet = None

    logging.info("Getting primary feed")

    feed = api.GetUserTimeline(screen_name=settings['user_id'],
                               since_id=last_found_tweet,
                               count=max_tweets,
                               include_rts=False)

    if len(feed) == 0:
        logging.info("No new tweets were found.")
        sys.exit(0)

    if last_found_tweet is not None:
        logging.info('found', len(feed), 'tweets since tweet.id = {}'.format(last_found_tweet))

    new_tweets = []
    reply_ids = []
    parsed_ids = []
    for tweet in feed:
        new_tweets.append(parse_tweet(tweet))
        reply_ids.append(tweet.in_reply_to_status_id)
        parsed_ids.append(tweet.id)

    # Get a list of the parent tweets not already grabbed
    parent_ids = [id for id in reply_ids if id not in parsed_ids]
    parent_ids = list(filter(lambda x: x is not None, parent_ids))

    # Only run if we have extra tweets to collect
    if len(parent_ids) != 0:
        logging.info('Getting originals from replies')
        feed = api.GetStatuses(parent_ids)

        logging.info('Found {} extra tweets inside threads of which the primary '
                     'user has replied.'.format(len(feed)))
        for tweet in feed:
            new_tweets.append(parse_tweet(tweet))

    sorted_tweets = sorted(new_tweets, key=lambda x: x.id, reverse=True)
    json_tweets = [tweet.to_dict() for tweet in sorted_tweets]

    jdb['tweets'] = json_tweets + jdb['tweets']

    logging.info('Saving to database')
    with open(db_file, 'w') as f:
        json.dump(jdb, f)

    logging.info('Database now stands at {} captured tweets'.format(len(jdb['tweets'])))
