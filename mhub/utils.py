from twisted.python import log


class Logger(object):

    """ Logging utility class """

    # 60:TRACE 50:DEBUG 40:INFO 30:WARN 20:ERROR 10:FATAL

    LEVELS = {60: "TRACE", 50: "DEBUG", 40: "INFO",
              30: "WARN", 20: "ERROR", 10: "FATAL"} 


    def __init__(self, 
                 name="default", 
                 producer=None,
                 level=40):

        """ Constructor """

        self.name = name
        self.producer = producer
        self.level = level


    def log(self, 
            message, 
            severity=40,
            publish=False):

        """ Message handler """

        # if severity >= self.level: return

        level_name = self.LEVELS.get(severity).upper()
        level_short = level_name[0]

        msg = "%s [%s]: %s" % (level_short, self.name, message)
        log.msg(msg)

        """

        if publish:
            try:
                self.producer.publish({
                    "action": "xmpp.send",
                    "params": {
                        "recipient": "jinglemansweep@gmail.com",
                        "body": msg
                    }
                })
            except:
                pass

        """

    def debug(self, 
              message,
              publish=False):

        """ Debug message """

        self.log(message, 
                 severity=50, 
                 publish=publish)


    def info(self, 
             message,
             publish=False):

        """ Info message """

        self.log(message, 
                 severity=40,
                 publish=publish)


    def warn(self, 
             message,
             publish=False):

        """ Warn message """

        self.log(message, 
                 severity=30,
                 publish=publish)


    def error(self, 
              message,
              publish=False):

        """ Error message """

        self.log(message, 
                 severity=20,
                 publish=publish)


    def fatal(self,
              message,
              publish=False):

        """ Fatal message """

        self.log(message, 
                 severity=10,
                 publish=publish)
