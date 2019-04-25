#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import json
import logging
import os
import sys
import twitter

from twitter_saver.configuration import Configuration
from twitter_saver.objects import parse_tweet

logging.basicConfig(level=logging.INFO)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--configuration", "-c", help="the path to the config folder", type=str)
    parser.add_argument("--verbose", "-v", help="enable verbose logging", type=bool, default=False)

    args = parser.parse_args()
    if args.configuration is None:
        logging.warning(parser.format_help())
        raise FileNotFoundError("You have not specified a configuration path")

    yaml_conf = os.path.join(args.configuration, "configuration.yml")

    conf = Configuration(yaml_conf)

    logging.info("Grabbing all new tweets for user: {}".format(conf.screen_name))

    db_file = os.path.join(conf.save_path, "tweets-db.json")

    api = twitter.Api(consumer_key=conf.consumer_key,
                      consumer_secret=conf.consumer_secret,
                      access_token_key=conf.access_token,
                      access_token_secret=conf.access_token_secret,
                      tweet_mode="extended")

    # Database file (JSON)
    try:
        with open(db_file, "r") as f:
            jdb = json.load(f)
            # Sort the database to get the last known tweet
            db_tweet_ids = sorted([tweet.get("id") for tweet in jdb.get("tweets")])
            last_found_tweet = str(db_tweet_ids[-1])
    except FileNotFoundError:
        logging.warning("Database not found, creating new file...")
        jdb = {"tweets": []}
        last_found_tweet = None

    logging.info("Getting primary feed")

    feed = api.GetUserTimeline(screen_name=conf.screen_name,
                               since_id=last_found_tweet,
                               count=conf.max_tweets,
                               include_rts=False)

    if len(feed) == 0:
        logging.info("No new tweets were found.")
        sys.exit(0)

    if last_found_tweet is not None:
        logging.info("Found {} tweets since tweet.id = {}".format(len(feed), last_found_tweet))

    new_tweets = []
    reply_ids = []
    parsed_ids = []

    logging.info("Parsing tweets.")
    for tweet in feed:
        new_tweets.append(parse_tweet(tweet))
        reply_ids.append(tweet.in_reply_to_status_id)
        parsed_ids.append(tweet.id)

    # Get a list of the parent tweets not already grabbed
    parent_ids = [id for id in reply_ids if id not in parsed_ids]
    parent_ids = list(filter(lambda x: x is not None, parent_ids))

    # Only run if we have extra tweets to collect
    if len(parent_ids) != 0:
        logging.info("Getting tweets upstream from replies")
        feed = api.GetStatuses(parent_ids)

        logging.info("Found {} upstream tweets.".format(len(feed)))
        for tweet in feed:
            new_tweets.append(parse_tweet(tweet))

    logging.info("Downloading all media items")
    for tweet in new_tweets:
        for media in tweet.media:
            media.get_media(conf.media_path)

    sorted_tweets = sorted(new_tweets, key=lambda x: x.id, reverse=True)
    json_tweets = [tweet.to_dict() for tweet in sorted_tweets]

    jdb["tweets"] = json_tweets + jdb["tweets"]

    logging.info("Saving to database")
    with open(db_file, "w") as f:
        json.dump(jdb, f)

    logging.info("Database now stands at {} captured tweets.".format(len(jdb["tweets"])))
