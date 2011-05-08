import datetime

class Plugin(object):

    """ Logic Processor Plugin """

    def __init__(self, cfg, publisher, logger):

        """ Constructor """

        self.cfg = cfg
        self.publisher = publisher
        self.logger = logger

        self.scripts = dict()
        self.env = dict()
        self.state = dict()


    def on_init(self):

        """ Main plugin initialisation """

        self.setup_scripts()
        

    def on_tick(self):

        """ On tick handler """

        ctx = self.get_context()

        for script in self.scripts.get("on_tick"):
            exec(script, ctx)

        #self.logger.debug("State:")
        #self.logger.debug(self.state)
        

    def on_message(self, data, message):

        """ On AMQP message handler """

        ctx = self.get_context()
        ctx["message"] = data

        for script in self.scripts.get("on_message"):
            exec(script, ctx)

        self.state = ctx.get("state")


    def get_context(self):

        """ Gets the context used in script processing """

        ctx = {
            "state": self.state,
            "env": self.get_environment(),
            "logger": self.logger,
            "send_message": self.publisher.send
        }
        return ctx


    def get_environment(self):

        """ Update read-only environment with useful data (datetime etc.) """

        dt = datetime.datetime.now()

        env = {}
        env["datetime"] = {"year": dt.year, "month": dt.month, "day": dt.day,
                           "hour": dt.hour, "minute": dt.minute, "second": dt.second}

        return env


    def setup_scripts(self):

        """ Setup configured init, timed and event scripts """

        scripts = self.cfg.get("scripts", dict())

        on_init = scripts.get("on_init", list())
        on_message = scripts.get("on_message", list())
        on_tick = scripts.get("on_tick", list())

        for trigger, scripts in scripts.iteritems():
            for filename in scripts:
                fh = open(filename, "r")
                contents = "".join(fh.readlines())
                if not trigger in self.scripts:
                    self.scripts[trigger] = list()
                self.scripts[trigger].append(contents)