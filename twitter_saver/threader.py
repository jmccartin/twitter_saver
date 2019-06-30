import argparse
import json
import logging
import os

from twitter_saver.configuration import Configuration
from twitter_saver.objects import Tweet
from twitter_saver.utils import create_threads

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

# Database file (JSON)
try:
    with open(db_file, "r") as f:
        jdb = json.load(f)
        logging.info("Loaded tweet database")
except FileNotFoundError:
    logging.error("Database not found!")
    raise

all_tweets = []

for j_tweet in jdb["tweets"]:
    tweet = Tweet.new_from_json(j_tweet)
    all_tweets.append(tweet)

threads = create_threads(all_tweets)

# Write the threads to a json file (pretty format)
with open(os.path.join(conf.save_path, "tweets-threaded.json"), "w") as f:
    thread_json = {"threads": []}
    for i, thread in enumerate(threads):
        thread_list = [tweet.to_dict().pop("_json", None) for tweet in thread]
        thread_json["threads"].append({"id": i + 1, "tweets": thread_list})
    print(thread_json)
    json.dump(thread_json, f, indent=4, sort_keys=True)
