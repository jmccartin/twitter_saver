import argparse
import json
import logging
import math
import os
from PIL import Image
import shutil
import twitter
import urllib.request

from twitter_saver.configuration import Configuration
from twitter_saver.latex_functions import *
from twitter_saver.objects import Tweet
from twitter_saver.utils import create_threads, format_timestamp, clean_text

parser = argparse.ArgumentParser()
parser.add_argument("--configuration", "-c", help="the path to the config folder", type=str)
parser.add_argument("--log", "-l", help="set the logging level", type=str, default="INFO")

args = parser.parse_args()
if args.configuration is None:
    print(parser.format_help())
    raise FileNotFoundError("You have not specified a configuration path")

numeric_level = getattr(logging, args.log.upper(), None)
if not isinstance(numeric_level, int):
    raise ValueError("Invalid log level: {}".format(args.log))

logging.basicConfig(level=numeric_level,
                    format="%(asctime)s [%(levelname)s] %(message)s",
                    datefmt='%Y-%m-%d %H:%M:%S'
                    )

yaml_conf = os.path.join(args.configuration, "configuration.yml")

conf = Configuration(yaml_conf)

db_file = os.path.join(conf.save_path, "tweets-db.json")
user_db_file = os.path.join(conf.save_path, "users-db.json")

# Get a copy of the twitter logo for LaTeX doc front page
if not os.path.exists(os.path.join(conf.media_path, "twitter_logo.png")):
    url = ("https://upload.wikimedia.org/wikipedia/en/thumb/9/9f/"
           "Twitter_bird_logo_2012.svg/295px-Twitter_bird_logo_2012.svg.png")
    urllib.request.urlretrieve(url, os.path.join(conf.media_path, "twitter_logo.png"))

# Database file (JSON)
try:
    with open(db_file, "r") as f:
        jdb = json.load(f)
        logging.info("Loaded tweet database")
except FileNotFoundError:
    logging.error("Database not found!")
    raise

api = twitter.Api(consumer_key=conf.consumer_key,
                  consumer_secret=conf.consumer_secret,
                  access_token_key=conf.access_token,
                  access_token_secret=conf.access_token_secret,
                  tweet_mode="extended")

all_tweets = []

for j_tweet in jdb["tweets"]:
    tweet = Tweet.new_from_json(j_tweet)
    all_tweets.append(tweet)

threads = create_threads(all_tweets)

# Users Database file (JSON)
try:
    with open(user_db_file, "r") as f:
        user_dict = json.load(f)
        logging.info("Loaded user database")
except FileNotFoundError:
    user_dict = {}
    logging.info("Creating new user database")


def get_user_data(screen_name):
    if screen_name not in user_dict:
        logging.debug("Looking up profile info for user: {}".format(screen_name))
        try:
            user = api.GetUser(screen_name=screen_name, include_entities=True)
        except twitter.error.TwitterError:
            default = conf.settings.get("default_user_image")
            user = twitter.User(screen_name=screen_name, profile_image_url=default)
        profile_picture = "profile/{}.jpg".format(screen_name)

        path = os.path.join(conf.profile_path, "{}.jpg".format(screen_name))
        if not os.path.exists(path):
            urllib.request.urlretrieve(user.profile_image_url, path)
        user_dict[screen_name] = {}
        user_dict[screen_name]["name"] = user.name
        user_dict[screen_name]["profile_picture"] = profile_picture

    return user_dict[screen_name]


tex_file = os.path.join(conf.save_path, "tweets.tex")
shutil.copyfile(os.path.join("twitter_saver", "resources", "header.tex"), tex_file)


def calculate_margins(tweet):
    text_margin = 0.7 + 0.5 * math.floor(len(tweet.text) / 82)
    picture_margin = []
    for img in tweet.media:
        file_path = os.path.join(conf.media_path, img.filename)
        if not os.path.exists(file_path):
            logging.warning("File {} not found in media path!".format(file_path))
        (width, height) = Image.open(file_path).size
        picture_margin.append((12.5 / width) * height)
    picture_margin = sum(picture_margin)
    return text_margin + picture_margin


with open(tex_file, "a") as f:
    f.write(titleTeX.format(screenName=conf.screen_name,
                            fromDate=format_timestamp(threads[0][0].created_at),
                            toDate=format_timestamp(threads[-1][-1].created_at)))
    logging.info("Creating LaTeX file from threads")
    for thread in threads:
        if "Mechanical" in thread[0].text:
            print(thread[0])
            print([t.id for t in thread])
        f.write("% ---------------- THREAD ---------------\n")
        for i, tweet in enumerate(thread):
            # Don"t print a thread line for last tweet
            if tweet == thread[-1]:
                threadLine = ""
            else:
                modifier = "{0:.2f}".format(calculate_margins(tweet))
                threadLine = threadTeX.format(modifier)
            media_str = " ".join(mediaTeX.format(m.filename) for m in tweet.media) \
                        + "\n\\vspace{10pt}\n"
            f.write(tweetTeX.format(get_user_data(tweet.author).get("profile_picture"),
                                    threadLine,
                                    clean_text(get_user_data(tweet.author).get("name")),
                                    "@" + clean_text(tweet.author),
                                    format_timestamp(tweet.created_at),
                                    clean_text(tweet.text),
                                    media_str,
                                    len(thread) - (i + 1)
                                    ))
            f.write("\n\n")  # Force a new line between each tweet
        f.write(ruleTeX)
        f.write("% ---------------------------------------\n\n")
    f.write("\n\\end{document}")

with open(user_db_file, "w") as f:
    json.dump(user_dict, f)

logging.info("Finished creating LaTeX file")
