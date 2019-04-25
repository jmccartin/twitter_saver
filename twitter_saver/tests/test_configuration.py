from twitter_saver.configuration import Configuration


def test_configuration():
    conf = Configuration("conf/configuration-defaults.yml")

    assert type(conf.screen_name) == str, "The param: screen_name was not a string!"
    assert type(conf.max_tweets) == int, "The param: max_tweets was not an int!"
