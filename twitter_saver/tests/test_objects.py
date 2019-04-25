from twitter import Status
from twitter_saver.objects import parse_tweet

import pytest


def test_parse_tweets():
    media_json = {
        "id": 1,
        "filename": "a.jpg",
        "media_url": "https://domain/a.jpg",
        "type": "photo"
    }

    tweet_json = {
        "id": 1,
        "user": {"id": 1, "screen_name": "nobody"},
        "in_reply_to": "someone else",
        "in_reply_to_status_id": 0,
        "text": "Hello, World!",
        "entities": {"media": [media_json]}
    }

    status = Status().NewFromJsonDict(tweet_json)
    tweet = parse_tweet(status)

    assert tweet.id == 1, "The parsed tweet's ID did not match what was expected!"
    assert tweet.media[0].filename == "a.jpg", "The expected filename was not correct!"
