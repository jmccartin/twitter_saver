import os
from typing import List
import urllib.request


class TwitterObject:

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
                 id: str,
                 url: str,
                 filename: str,
                 type: str):
        super(MediaItem, self).__init__()
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
                 id: str = None,
                 created_at: str = None,
                 author: str = None,
                 in_reply_to: str = None,
                 in_reply_to_status_id: str = None,
                 text: str = None,
                 media: List[MediaItem] = None):
        super(Tweet, self).__init__()
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
    def __init__(self, **kwargs):
        self.param_defaults = {
            'author': None,
            'screen_name': None,
            'profile_picture': None,
        }

        for (param, default) in self.param_defaults.items():
            setattr(self, param, kwargs.get(param, default))
