import datetime
import twitter


class Plugin(object):

    """ Twitter Poster Plugin """

    name = "twitter"
    description = "Twitter integration"
    author = "MHub"
    
        
    def on_init(self):

        """ Main plugin initialisation """

        self.api = twitter.Api(consumer_key=self.cfg.get("consumer_key"),
                               consumer_secret=self.cfg.get("consumer_secret"),
                               access_token_key=self.cfg.get("access_token_key"),
                               access_token_secret=self.cfg.get("access_token_secret"))

        self.tasks = [(self.cfg.get("poll_interval", 60), self.get_tweets)]

        self.last_poll = dict()
        self.first_run = True


    def get_tweets(self):

        """ Gets tweets from configured timelines """

        timelines = self.cfg.get("timelines")

        for user in timelines:
            self.last_poll[user] = 0
            try:
                statuses = self.api.GetUserTimeline(user)
                for status in statuses:
                    ts = status.created_at_in_seconds
                    if self.first_run or ts >= self.last_poll[user]:
                        self.producer.publish({
                            "action": "%s.input" % (self.name),
                            "params": {"user": user, "body": status.text}
                        })
                        self.last_poll[user] = ts + 1
            except twitter.TwitterError as e:
                self.logger.warn("Twitter API error: %s" % (e))
        self.first_run = False
        

    def on_message(self, data, message):

        """ On AMQP message handler """

        action, params = data.get("action"), data.get("params")

        if action == "%s.action" % (self.name):

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
