import datetime
import functools
from typing import List
import urllib.request

from src.python.main.objects import Tweet


def create_threads(tweets: List[Tweet]) -> List[List[Tweet]]:
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


def format_timestamp(timestamp: str) -> str:
    try:
        mydate = datetime.datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
    except ValueError:
        mydate = datetime.datetime.strptime(timestamp, '%a %b %d %H:%M:%S %z %Y')
    return mydate.strftime("%b %d %Y")


def clean_text(text: str) -> str:
    """
    Removes unwanted characters from a tweet's fulltext
    """
    for char in ['&', '#', '_', '%', '$', '{', '}']:
        text = str(text).replace(char, '\\{}'.format(char))
    return str(text)
