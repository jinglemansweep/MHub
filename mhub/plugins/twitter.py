import datetime
import twitter


class Plugin(object):

    """ Twitter Poster Plugin """

    def __init__(self, cfg, publisher, logger):

        """ Constructor """

        self.cfg = cfg
        self.publisher = publisher
        self.logger = logger
        

    def on_init(self):

        """ Main plugin initialisation """

        self.api = twitter.Api(consumer_key=self.cfg.get("consumer_key"),
                               consumer_secret=self.cfg.get("consumer_secret"),
                               access_token_key=self.cfg.get("access_token_key"),
                               access_token_secret=self.cfg.get("access_token_secret"))


    def on_message(self, data, message):

        """ On AMQP message handler """

        action, params = data.get("action"), data.get("params")

        if action == "tweet":

            body = params.get("body", "No Body")

            self.logger.info("Sending Tweet")
            self.send_tweet(body)


    def send_tweet(self, body):

        self.logger.debug("Body: %s" % (body))

        try:
            status = self.api.PostUpdate(body)
        except UnicodeDecodeError:
            pass
        except twitter.TwitterError as e:
            self.logger.warn("Twitter API error: %s" % (e))