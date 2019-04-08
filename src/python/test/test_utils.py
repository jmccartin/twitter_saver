import pytest

from src.python.main.objects import Tweet
from src.python.main.utils import create_threads

data = [
    # Thread 1
    (1, "Thu Mar 28 00:00:00 +0000 2019", None),
    (2, "Thu Mar 28 00:01:00 +0000 2019", 1),
    # Thread 2
    (3, "Thu Mar 28 00:02:00 +0000 2019", None),
    (4, "Thu Mar 28 00:03:00 +0000 2019", 3),
    # Thread 1
    (5, "Thu Mar 28 00:04:00 +0000 2019", 2),
    (6, "Fri Mar 29 00:03:00 +0000 2019", 5),
    (7, "Fri Mar 29 00:05:00 +0000 2019", 6),
    # Thread 3
    (8, "Fri Mar 30 00:00:00 +0000 2019", None),
    (9, "Fri Mar 30 00:01:00 +0000 2019", 8),
]


def test_create_threads():
    tweets = [Tweet(id=entry[0], created_at=entry[1], in_reply_to_status_id=entry[2])
              for entry in data]

    threads = create_threads(tweets)

    assert len(threads) == 3, "The number of threads were not 3!"
    assert [t.id for t in threads[0]] == [1, 2, 5, 6, 7],\
        "The expected ids in thread 1 were not present!"
    assert len(threads[1]) == 2, "The length of the second thread was not 2!"
    assert threads[-1][-1].id == data[-1][0], "The tweets are not in order!"
