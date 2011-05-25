


class Plugin(object):

    """ Schedule Plugin """

    def __init__(self, cfg, publisher, logger):

        """ Constructor """

        self.cfg = cfg
        self.publisher = publisher
        self.logger = logger
        

    def on_init(self):

        """ Main plugin initialisation """

        self.tasks = [(5.0, self.process_schedules)]
        self.last_poll = dict()
        self.first_run = True

        
    def process_schedules(self):

        schedules = self.cfg.get("schedules")

        #for name, schedule in schedules.iteritems():
        #    print name
