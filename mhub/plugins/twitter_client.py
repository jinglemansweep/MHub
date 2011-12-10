import logging
from oauth import oauth
from twisted.internet import defer, task
from twisted.internet.task import LoopingCall
from twittytwister import twitter


from base import BasePlugin




class TwitterPlugin(BasePlugin):

    """
    Twitter plugin.
    """

    default_config = {
        "enabled": False,
        "consumer_key": "czjLv9TriwG8hZecPRsVA",
        "consumer_secret": "T5XYR3MIWcTVBe4V4ENrWBPeUSwChKz950xvrUoz98",
        "access_token": "changeme",
        "access_token_secret": "changeme",
        "timeline": "bbcnews"
    }
    

    def setup(self, cfg):

        BasePlugin.setup(self, cfg)

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

        self.state.remove({"_id": self.state_key("tweet_ids")})


    def poll_tweets(self):

        try:
            self.tw.user_timeline(self.got_tweet,
                                  self.timeline)
        except KeyError, e:
            self.logger.debug("Failed to poll tweets")

    def got_tweet(self, msg):

        tweet_ids = self.state_get("tweet_ids", list())
        
        if msg.id not in tweet_ids:
        
            tweet_ids.append(msg.id)

            self.publish_event("new_tweet", {
                "id": msg.id,
                "body": msg.text,
                "source": msg.source,
                "geo": msg.geo,
                "created_at": msg.created_at
            })

        self.state_save("tweet_ids", tweet_ids)

