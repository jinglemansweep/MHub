import datetime
import os

class Plugin(object):

    """ Logic Processor Plugin """

    name = "logic_processor"
    description = "Simple user script logic processor"
    author = "MHub"
    

    def on_init(self):

        """ Main plugin initialisation """

        self.tasks = [(0.1, self.on_tick)]

        self.scripts = dict()
        self.env = dict()
        self.state = dict()

        self.setup_scripts()
        

    def on_tick(self):

        """ On tick handler """

        ctx = self.get_context()

        for script in self.scripts.get("on_tick", list()):
            exec(script, ctx)

        #self.logger.debug("State:")
        #self.logger.debug(self.state)
        

    def on_message(self, data, message):

        """ On AMQP message handler """

        ctx = self.get_context()
        ctx["message"] = data


        for script in self.scripts.get("on_message", list()):
            exec(script, ctx)

        self.state = ctx.get("state")


    def get_context(self):

        """ Gets the context used in script processing """

        self.update_environment()

        ctx = {
            "state": self.state,
            "env": self.env,
            "logger": self.logger,
            "send_message": self.producer.publish
        }
        
        return ctx


    def update_environment(self):

        """ Update read-only environment with useful data (datetime etc.) """

        dt = datetime.datetime.now()

        env = self.env

        if not "datetime" in env: env["datetime"] = {}

        for interval in ["year", "month", "day", "hour", "minute", "second"]:
            current = getattr(dt, interval)
            env["datetime"]["new_%s" % (interval)] = ((env.get("datetime").get(interval, current) != current))
            env["datetime"][interval] = current

        env["datetime"]["datestamp"] = dt.strftime("%Y%m%d")
        env["datetime"]["year_month"] = dt.strftime("%Y%m")
        env["datetime"]["month_day"] = dt.strftime("%m%d")
        env["datetime"]["timestamp"] = dt.strftime("%H%M%S")
        env["datetime"]["hour_minute"] = dt.strftime("%H%M")
        env["datetime"]["minute_second"] = dt.strftime("%M%S")

        self.env = env
        

    def setup_scripts(self):

        """ Setup configured init, timed and event scripts """

        scripts_path = os.path.expanduser(self.cfg.get("scripts_path"))
        
        scripts = self.cfg.get("scripts", dict())

        on_init = scripts.get("on_init", list())
        on_message = scripts.get("on_message", list())
        on_tick = scripts.get("on_tick", list())

        for trigger, scripts in scripts.iteritems():
            for filename in scripts:
                script_filename = os.path.join(scripts_path, filename)
                if os.path.exists(script_filename):
                    fh = open(script_filename, "r")
                    contents = "".join(fh.readlines())
                    if not trigger in self.scripts:
                        self.scripts[trigger] = list()
                    self.scripts[trigger].append(contents)
                else:
                    self.logger.debug("Script not found")
