import os
import twitter
from typing import List
import urllib.request


class TwitterObject:

    def __init__(self, id: int):
        self.id = id

    def __eq__(self, other):
        return self.id == other.id

    def from_dict(self, **entries) -> None:
        self.__dict__.update(entries)

    @classmethod
    def new_from_json(cls, data, **kwargs):
        """ Create a new instance based on a JSON dict. Any kwargs should be
        supplied by the inherited, calling class.

        Args:
            data: A JSON dict, as converted from the JSON in the twitter API.

        """

        json_data = data.copy()
        if kwargs:
            for key, val in kwargs.items():
                json_data[key] = val

        c = cls(**json_data)
        c._json = data
        return c


class MediaItem(TwitterObject):
    def __init__(self,
                 id: int,
                 url: str,
                 filename: str,
                 type: str):
        super(MediaItem, self).__init__(id)
        self.id = id
        self.url = url
        self.filename = filename
        self.type = type

    def __repr__(self):
        return "Media(ID={media_id}, Type={media_type}, DisplayURL='{url}')".format(
            media_id=self.id,
            media_type=self.type,
            url=self.url)

    def get_media(self, media_path: str) -> None:
        """
        Saves an online media object (i.e, image) to a specific location
        :param media_path: path to save the media object
        """
        urllib.request.urlretrieve(self.url, os.path.join(media_path, self.filename))


class Tweet(TwitterObject):
    def __init__(self,
                 id: int = None,
                 created_at: str = None,
                 author: str = None,
                 in_reply_to: str = None,
                 in_reply_to_status_id: str = None,
                 text: str = None,
                 media: List[MediaItem] = None):
        super(Tweet, self).__init__(id)
        self.id = id
        self.created_at = created_at
        self.author = author
        self.in_reply_to = in_reply_to
        self.in_reply_to_status_id = in_reply_to_status_id
        self.text = text
        if media is not None:
            if len(media) != 0:
                if type(media[0]) == MediaItem:
                    self.media = media
                elif type(media[0]) == dict:
                    self.media = [self.new_from_json(m) for m in media]
            else:
                self.media = media
        else:
            self.media = []

    def __repr__(self):
        return "Tweet(ID={tweet_id}, Author={author}, Text='{text}...')".format(
            tweet_id=self.id,
            author=self.author,
            text=self.text)

    @classmethod
    def new_from_json(cls, data, **kwargs):
        """ Create a new instance based on a JSON dict.

        Args:
            data: A JSON dict, as converted from the JSON in the twitter API

        Returns:
            A twitter.Status instance
        """
        media = None

        if 'media' in data.keys():
            media = [MediaItem.new_from_json(m) for m in data['media']]

        return super(cls, cls).new_from_json(data=data, media=media)

    def to_dict(self) -> dict:
        """
        Produces a dict object of the tweet for use in saving to a json database
        :return: dict object
        """

        json_dict = {}

        for (key, value) in self.__dict__.items():
            if key == "media" and len(value) != 0:
                media_list = []
                for media in value:
                    if isinstance(value[0], MediaItem):
                        media_list.append(media.__dict__)
                    else:
                        media_list.append(media)
                json_dict["media"] = media_list
            else:
                json_dict[key] = value

        return json_dict


class User(TwitterObject):
    def __init__(self,
                 id,
                 author,
                 screen_name,
                 profile_picture):
        super(TwitterObject, self).__init__(id)
        self.author = author
        self.screen_name = screen_name
        self.profile_picture = profile_picture


def parse_tweet(tweet: twitter.Status) -> Tweet:
    """
    Converts each tweet (Status object from python-twitter)
    into a simplified format, while grabbing all media items
    on the fly.
    :param tweet: twitter.models.Status object
    :return: Tweet object
    """

    media_list = []

    if tweet.media is not None:
        for media in tweet.media:
            media_obj = MediaItem(id=media.id,
                                  filename=media.media_url.split("/")[-1],
                                  url=media.media_url,
                                  type=media.type)
            media_list.append(media_obj)

    if tweet.full_text is None:
        text = tweet.text
    else:
        text = tweet.full_text

    return Tweet(id=tweet.id,
                 created_at=str(tweet.created_at),
                 author=tweet.user.screen_name,
                 in_reply_to=tweet.in_reply_to_screen_name,
                 in_reply_to_status_id=tweet.in_reply_to_status_id,
                 text=text,
                 media=media_list)
