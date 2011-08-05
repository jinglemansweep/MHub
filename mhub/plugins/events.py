import datetime
import fnmatch

class Plugin(object):

    """ Events plugin """

    name = "events"
    description = "Event management plugin"
    author = "MHub"
            

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
            
