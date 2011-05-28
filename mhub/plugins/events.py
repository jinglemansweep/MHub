import datetime
import fnmatch

class Plugin(object):

    """ Events plugin """

    def __init__(self, cfg, producer, logger):

        """ Constructor """

        self.name = "events"
        self.description = "Event management plugin"
        self.author = "MHub"
        self.cfg = cfg
        self.producer = producer
        self.logger = logger
        self.tasks = list()
        

    def on_message(self, data, message):

        """ On AMQP message handler """

        action, params = data.get("action"), data.get("params")

        self.process_events(action, params)

        
    def on_init(self):

        """ On Init """

        self.events = self.cfg.get("events", list())


    def process_events(self, action, params):

        """ Event processor helper """

        for name, event in self.events.iteritems():

            triggers = event.get("triggers", list())
            actions = event.get("actions", list())

            match = False

            for trigger in triggers:

                if fnmatch.fnmatch(action, trigger):
                    match = True
                    break

            if match:

                for action in actions:

                    self.producer.publish({
                        "action": action.get("action"),
                        "params": action.get("params", dict())
                    })
            
