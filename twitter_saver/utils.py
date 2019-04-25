import datetime
from functools import reduce
from typing import List
import twitter

from twitter_saver.objects import MediaItem, Tweet


def split_media(tweet: Tweet) -> List[Tweet]:
    """
    Splits a tweet based on the number of media.
    This is for better LaTeX formatting, as more
    than two pictures can often overrun the page
    margins.
    """
    split_tweets = []
    tweet_dict = tweet.to_dict()
    for media in tweet_dict["media"]:
        tweet_dict["media"] = [media]
        print(tweet_dict)
        split_tweets.append(Tweet.new_from_json(tweet_dict))
    return split_tweets


def create_threads(tweets: List[Tweet]) -> List[List[Tweet]]:
    """
    Attempts to thread tweets based on their creation
    timestamp, and who replied to each tweet.

    :param tweets: The database collection of tweets (as a list)
    :return: A list of threaded tweets
    """
    split_media_bool = True

    tweets = sorted(tweets, key=lambda t: create_timestamp(t.created_at), reverse=False)

    def fold_group(acc: List[List[Tweet]], tweet: Tweet) -> List[List[Tweet]]:
        if acc == [[]]:
            return [[tweet]]
        else:
            next_tweet = acc[-1][-1]
            if next_tweet.id == tweet.in_reply_to_status_id:
                return [*acc[:-1], [*acc[-1], tweet]]
            else:
                return [*acc, [tweet]]

    def add_to_thread(thread, replies):
        # Get all tweets less than a week older than the last tweet of the thread
        inside_window = filter(lambda tweet:
                               calc_day_diff(tweet.created_at, thread[-1].created_at).days <= 7,
                               replies)

        # Check if the tweets in the window are in the thread
        for tweet in inside_window:
            if tweet.in_reply_to_status_id == thread[-1].id:
                tweet_set.add(tweet.id)
                # Split the tweet by the amount of media it has
                if split_media_bool and len(tweet.media) != 0:
                    for new_tweet in split_media(tweet):
                        thread.append(new_tweet)
                else:
                    thread.append(tweet)
            elif tweet not in remainder:
                remainder.append(tweet)

        return thread

    parents = [[tweet] for tweet in tweets if tweet.in_reply_to_status_id is None]
    replies = [tweet for tweet in tweets if tweet.in_reply_to_status_id is not None]

    tweet_set = set()
    remainder = []

    threads = []
    for thread in parents:
        threads.append(add_to_thread(thread, replies))

    tweets = [tweet for tweet in remainder if tweet.id not in tweet_set]

    parents = [[tweet] for tweet in tweets if tweet.in_reply_to_status_id in tweet_set]
    replies = [tweet for tweet in tweets if tweet.in_reply_to_status_id not in tweet_set]

    for thread in parents:
        threads.append(add_to_thread(thread, replies))

    return sorted(threads, key=lambda thread: create_timestamp(thread[0].created_at))


def create_timestamp(time: str) -> datetime.datetime:
    try:
        my_date = datetime.datetime.strptime(time, '%Y-%m-%d %H:%M:%S')
    except ValueError:
        my_date = datetime.datetime.strptime(time, '%a %b %d %H:%M:%S %z %Y')
    return my_date


def format_timestamp(timestamp: str) -> str:
    return create_timestamp(timestamp).strftime("%b %d %Y")


def calc_day_diff(time1: str, time2: str) -> datetime.timedelta:
    return create_timestamp(time1) - create_timestamp(time2)


def clean_text(text: str) -> str:
    """
    Removes unwanted characters from a tweet's fulltext
    """
    for char in ['&', '#', '_', '%', '$', '{', '}']:
        text = str(text).replace(char, '\\{}'.format(char))
    return str(text)
