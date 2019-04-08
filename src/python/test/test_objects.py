import pytest

from src.python.main.objects import Tweet

media_json = {
    "id": 1,
    "url": "http://google.com",
    "filename": "test.jpg",
    "type": "photo"
}

tweet_json = {
    "id": 1,
    "created_at": "Thu Mar 28 00:00:00 +0000 2019",
    "in_reply_to": "God",
    "in_reply_to_status_id": 0,
    "text": "Hello, World!",
    "media": [media_json]
}


def test_tweet():
    """
    Tests to see if a Tweet class can be initialised from a json/dict
    object, and if the same object can be returned using the inbuilt
    methods.
    """

    tweet = Tweet().new_from_json(tweet_json)

    assert tweet.to_dict().pop("_json") == tweet_json,\
        "The json tweet did not equal the output of the Tweet class"
