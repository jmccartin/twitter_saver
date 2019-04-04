import datetime
import functools
from typing import List
import urllib.request

from src.python.main.objects import Tweet


def create_threads_foldl(tweets: List[Tweet]) -> List[List[Tweet]]:
    """
    Attempts to thread tweets based on their creation
    timestamp, and who replied to each tweet.
    :return: A list of threaded tweets
    """

    def fold_group(acc: List[List[Tweet]], tweet: Tweet) -> List[List[Tweet]]:
        if acc == [[]]:
            return [[tweet]]
        else:
            next_tweet = acc[-1][-1]
            if next_tweet.in_reply_to_status_id == tweet.id:
                return [*acc[:-1], [*acc[-1], tweet]]
            else:
                return [*acc, [tweet]]

    chronological_tweets = sorted(tweets, key=lambda t: t.created_at, reverse=True)

    grouped_threads = functools.reduce(fold_group, chronological_tweets, [[]])

    sorted_threads = map(lambda thread: sorted(thread, key=lambda tweet: tweet.id), grouped_threads)

    sorted_collection = sorted(list(sorted_threads), key=lambda thread: thread[0].id)

    return sorted_collection


def create_threads(tweets: List[Tweet]) -> List[List[Tweet]]:
    """
    Attempts to thread tweets based on their creation
    timestamp, and who replied to each tweet.

    :param tweets: The database collection of tweets (as a list)
    :return: A list of threaded tweets
    """

    parents = [[tweet] for tweet in tweets if tweet.in_reply_to_status_id is None]
    replies = [tweet for tweet in tweets if tweet.in_reply_to_status_id is not None]

    threads = []
    for thread in parents:
        # Get all tweets less than a day older than the last tweet of the thread
        inside_window = filter(lambda tweet:
                               calc_day_diff(tweet.created_at, thread[-1].created_at).days == 0,
                               replies)
        # Check if the tweets in the window are in the thread
        for tweet in inside_window:
            if tweet.in_reply_to_status_id == thread[-1].id:
                thread.append(tweet)
        threads.append(thread)

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
