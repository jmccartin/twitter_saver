from twitter_saver.objects import Tweet, MediaItem
from twitter_saver.utils import clean_text, create_threads, format_timestamp, split_media

thread_data = [
    # Thread 1
    (1, "Thu Mar 28 00:00:00 +0000 2019", None),
    (2, "Thu Mar 28 00:01:00 +0000 2019", 1),
    # Thread 2
    (3, "Thu Mar 28 00:02:00 +0000 2019", None),
    (4, "Thu Mar 28 00:03:00 +0000 2019", 3),
    # Thread 1 - broken by thread 1
    (5, "Thu Mar 28 00:04:00 +0000 2019", 2),
    (6, "Fri Mar 29 00:03:00 +0000 2019", 5),
    (7, "Fri Mar 29 00:05:00 +0000 2019", 6),
    # Thread 3
    (8, "Fri Mar 30 00:00:00 +0000 2019", None),
    (9, "Fri Mar 30 00:01:00 +0000 2019", 8),
    # Thread 4
    (10, "Fri Mar 30 00:02:00 +0000 2019", 5),
    (11, "Fri Mar 30 00:10:00 +0000 2019", 10),
    # Thread 5 - branch from thread 1
    (12, "Fri Mar 30 00:12:00 +0000 2019", 5),
    (13, "Fri Mar 30 00:20:00 +0000 2019", 12),
    # Thread 6 - branch from thread 1
    (14, "Fri Mar 30 00:22:00 +0000 2019", 5),
    # Thread 5 - broken by thread 6
    (15, "Fri Mar 30 00:24:00 +0000 2019", 13),
]


def test_clean_text():
    text = "& # _ % $ { }"
    assert clean_text(text) == "\\& \\# \\_ \\% \\$ \\{ \\}", "The text was not properly cleaned!"


def test_create_threads():
    tweets = [Tweet(id=entry[0], created_at=entry[1], in_reply_to_status_id=entry[2])
              for entry in thread_data]

    threads = create_threads(tweets)

    assert len(threads) == 6, "The number of threads was not correct!"
    assert [t.id for t in threads[0]] == [1, 2, 5, 6, 7],\
        "The expected ids in thread 1 were not present!"
    assert [t.id for t in threads[4]] == [12, 13, 15], \
        "The expected ids in thread 6 were not present!"
    assert len(threads[1]) == 2, "The length of the second thread was not 2!"
    assert threads[-1][-1].id == 14, "The tweets are not in order!"


def test_split_tweets():
    media = [
        MediaItem(id=1, filename="a.jpg", url="a", type="photo"),
        MediaItem(id=2, filename="b.jpg", url="b", type="photo"),
        MediaItem(id=3, filename="c.jpg", url="c", type="photo"),
    ]

    tweets = split_media(Tweet(id=1, media=media))

    assert len(tweets) == 3, "The number of split tweets was not 3!"
    assert tweets[0].media[0].id == 1, "The ID of the first tweet's media was not 1!"


def test_format_timestamp():
    time_str = "2020-10-27 00:00:00"
    result_str = "Oct 27 2020"

    assert format_timestamp(time_str) == result_str, "The resultant date format was not correct!"
