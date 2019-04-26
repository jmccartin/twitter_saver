import os
import yaml


class Configuration:
    def __init__(self, config_file):
        with open(config_file, "r") as f:
            conf = yaml.safe_load(f)

        self.settings = conf.get("general")

        self.screen_name = self.settings["screen_name"]
        self.max_tweets = self.settings["max_tweets"]

        self.save_path = self._get_path(self.settings.get("save_path"), self.screen_name)
        self.media_path = self._get_path(self.save_path, "media")
        self.profile_path = self._get_path(self.media_path, "profile")

        credentials = conf.get("credentials")
        self.consumer_key = credentials["consumer_key"]
        self.consumer_secret = credentials["consumer_secret"]
        self.access_token = credentials["access_token"]
        self.access_token_secret = credentials["access_secret"]

    def _get_path(self, path, name):
        full_path = os.path.join(path, name)

        if not os.path.exists(full_path):
            os.makedirs(full_path)

        return full_path
