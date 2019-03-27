#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import json
import logging
import math
import os
from PIL import Image
import shutil
from tqdm import tqdm
import twitter
from twitter.error import TwitterError
import urllib.request
import yaml

from src.python.main.objects import Tweet
from src.python.main.utils import create_threads, format_timestamp, clean_text

logging.basicConfig(level=logging.INFO)

parser = argparse.ArgumentParser()
parser.add_argument('--configuration', '-c', help="the path to the config folder", type=str)
parser.add_argument('--verbose', '-v', help="enable verbose logging", type=bool, default=False)

args = parser.parse_args()
if args.configuration is None:
    print(parser.format_help())
    raise FileNotFoundError("You haven't specified a configuration path")

yaml_conf = os.path.join(args.configuration, 'configuration.yml')

with open(yaml_conf, 'r') as f:
    conf = yaml.load(f)
    if args.verbose:
        print(yaml.dump(conf, default_flow_style=False))

settings = conf.get('general')
user_id = settings['user_id']

save_path = os.path.join(settings.get('save_path'), user_id)
media_path = os.path.join(save_path, 'media')
profile_path = os.path.join(media_path, 'profile')
db_file = os.path.join(save_path, 'db-{}.json'.format(user_id))
user_db_file = os.path.join(save_path, 'users-db.json')

if not os.path.exists(profile_path):
    os.makedirs(profile_path)

# Get a copy of the twitter logo for LaTeX doc front page
if not os.path.exists(os.path.join(media_path, "twitter_logo.png")):
    url = ("https://upload.wikimedia.org/wikipedia/en/thumb/9/9f/"
           "Twitter_bird_logo_2012.svg/295px-Twitter_bird_logo_2012.svg.png")
    urllib.request.urlretrieve(url, os.path.join(media_path, "twitter_logo.png"))

# Database file (JSON)
try:
    with open(db_file, 'r') as f:
        jdb = json.load(f)
except FileNotFoundError:
    logging.error("Database not found!")
    raise

# Load credentials from json file
creds = conf.get('credentials')

consumer_key = creds['consumer_key']
consumer_secret = creds['consumer_secret']
access_token = creds['access_token']
access_token_secret = creds['access_secret']

api = twitter.Api(consumer_key=consumer_key,
                  consumer_secret=consumer_secret,
                  access_token_key=access_token,
                  access_token_secret=access_token_secret)


all_tweets = []

for j_tweet in jdb['tweets']:
    tweet = Tweet.new_from_json(j_tweet)
    all_tweets.append(tweet)

threads = create_threads(all_tweets)


# Users Database file (JSON)
try:
    with open(user_db_file, 'r') as f:
        user_dict = json.load(f)
        logging.info("Loaded user database")
except FileNotFoundError:
    user_dict = {}
    logging.info("Creating new user database")


def get_user_data(screen_name):
    if screen_name not in user_dict:
        logging.debug('Looking up profile info for user: {}'.format(screen_name))
        try:
            user = api.GetUser(screen_name=screen_name, include_entities=True)
        except TwitterError:
            default = settings.get('default_user_image')
            user = twitter.User(screen_name=screen_name, profile_image_url=default)
        profile_picture = "profile/{}.jpg".format(screen_name)

        path = os.path.join(profile_path, "{}.jpg".format(screen_name))
        if not os.path.exists(path):
            urllib.request.urlretrieve(user.profile_image_url, path)
        user_dict[screen_name] = {}
        user_dict[screen_name]['name'] = user.name
        user_dict[screen_name]['profile_picture'] = profile_picture

    return user_dict[screen_name]


tex_file = os.path.join(save_path, 'tweets.tex')
shutil.copyfile(os.path.join('doc', 'header.tex'), tex_file)

tweetTeX = "\\tweet{{{}}}{{{}}}{{{}}}{{{}}}{{{}}}{{{}}}{{{}}}{{{}}}"
mediaTeX = "\\tweetmedia{{{}}}"
threadTeX = "\\threadline{{{}}}"
ruleTeX = "\\threadrule\n"


def calculate_margins(tweet):
    text_margin = 0.7 + 0.5 * math.floor(len(tweet.text) / 82)
    picture_margin = []
    for img in tweet.media:
        file_path = os.path.join(media_path, img.filename)
        if not os.path.exists(file_path):
            logging.warning("File {} not found in media path!".format(file_path))
        (width, height) = Image.open(file_path).size
        picture_margin.append((12.5/width)*height)
    picture_margin = sum(picture_margin)
    return text_margin + picture_margin


with open(tex_file, 'a') as f:
    logging.info("Creating LaTeX file from threads")
    for thread in tqdm(threads):
        f.write("% ---------------- THREAD ---------------\n")
        for i, tweet in enumerate(thread):
            # Don't print a thread line for last tweet
            if tweet == thread[-1]:
                threadLine = ""
            else:
                modifier = "{0:.2f}".format(calculate_margins(tweet))
                threadLine = threadTeX.format(modifier)
            media_str = " ".join(mediaTeX.format(m.filename) for m in tweet.media) \
                        + "\n\\vspace{10pt}\n"
            f.write(tweetTeX.format(get_user_data(tweet.author).get('profile_picture'),
                                    threadLine,
                                    clean_text(get_user_data(tweet.author).get('name')),
                                    "@" + clean_text(tweet.author),
                                    format_timestamp(tweet.created_at),
                                    clean_text(tweet.text),
                                    media_str,
                                    len(thread)-(i+1)
                                    ))
            f.write("\n\n")  # Force a new line between each tweet
        f.write(ruleTeX)
        f.write("% ---------------------------------------\n\n")
    f.write("\n\\end{document}")

with open(user_db_file, 'w') as f:
    json.dump(user_dict, f)

logging.info("Finished creating LaTeX file")
