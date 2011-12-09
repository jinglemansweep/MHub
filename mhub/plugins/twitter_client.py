import logging
from oauth import oauth
from twisted.internet import defer, task
from twisted.internet.task import LoopingCall
from twittytwister import twitter


from base import BasePlugin




class TwitterPlugin(BasePlugin):

    """
    Twitter plugin.

    :param name: Name of plugin.
    :type name: str.
    :param cls: Class/type of plugin.
    :type cls: str.
    :param service: Container service.
    :type service: mhub.service.
    :param cfg: Plugin configuration dictionary.
    :type cfg: dict.
    """

    def __init__(self, name, cls, service, cfg):

        BasePlugin.__init__(self, name, cls, service, cfg)

        logging.getLogger("twittytwister").setLevel(logging.ERROR)
        
        self.consumer_key = self.cfg.get("consumer_key")
        self.consumer_secret = self.cfg.get("consumer_secret")
        self.access_token = self.cfg.get("access_token")
        self.access_token_secret = self.cfg.get("access_token_secret")
        self.timeline = self.cfg.get("timeline")

        self.consumer = oauth.OAuthConsumer(self.consumer_key,
                                            self.consumer_secret)

        self.token = oauth.OAuthToken(self.access_token,
                                      self.access_token_secret)

        self.tw = twitter.Twitter(consumer=self.consumer,
                                  token=self.token)

        poll_task = LoopingCall(self.poll_tweets)
        poll_task.start(self.cfg.get("poll_interval", 60))

        self.store_del("tweet_ids")        


    def poll_tweets(self):
        
        self.tw.user_timeline(self.got_tweet,
                              self.timeline)


    def got_tweet(self, msg):

        tweets = self.store_get("tweet_ids", list())

        if msg.id not in tweets:
        
            tweets.append(msg.id)

            self.publish_event("new_tweet", {
                "id": msg.id,
                "body": msg.text,
                "source": msg.source,
                "geo": msg.geo,
                "created_at": msg.created_at
            })

        self.store_put("tweet_ids", tweets)

