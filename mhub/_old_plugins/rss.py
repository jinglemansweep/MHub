import datetime
import feedparser

from twisted.python import log


class Plugin(object):

    """ RSS Feed Plugin """


    name = "rss"
    description = "RSS feed integration"
    author = "MHub"

    default_config = {
        "feeds": ["http://feeds.bbci.co.uk/news/rss.xml"],
        "poll_interval": 300
    }


    def on_init(self):

        """ Main plugin initialisation """

        self.tasks = [(self.config.get("poll_interval", 60), self.get_feeds)]
        self.last_poll = dict()
        self.first_run = True

        
    def get_feeds(self):

        """ RSS feed parser helper """

        feeds = self.config.get("feeds", list())

        for url in feeds:

            self.last_poll[url] = datetime.datetime.now()
            feed = feedparser.parse(url)

            for entry in feed.entries:

                ets = entry.date_parsed
                ts = datetime.datetime(*ets[:7])

                if self.first_run or ts >= self.last_poll[url]:

                    msg = {
                        "action": "input",
                        "params": {
                            "feed": url,
                            "title": entry.title,
                            "description": entry.description,
                            "link": entry.link
                        }
                    }
                    self.send_amqp_message(msg)

                    self.last_poll[url] = ts

        self.first_run = False
