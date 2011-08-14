from twisted.python import log


class Logger(object):

    """ Logging utility class """

    # 60:TRACE 50:DEBUG 40:INFO 30:WARN 20:ERROR 10:FATAL

    LEVELS = {60: "TRACE", 50: "DEBUG", 40: "INFO",
              30: "WARN", 20: "ERROR", 10: "FATAL"} 


    def __init__(self, name="default", level=40):

        """ Constructor """

        self.name = name
        self.level = level


    def log(self, message, severity=40):

        """ Message handler """

        # if severity >= self.level: return

        level_name = self.LEVELS.get(severity).upper()
        level_short = level_name[0]

        log.msg("%s [%s]: %s" % (level_short, self.name, message))


    def debug(self, message):

        """ Debug message """

        self.log(message, severity=50)


    def info(self, message):

        """ Info message """

        self.log(message, severity=40)


    def warn(self, message):

        """ Warn message """

        self.log(message, severity=30)


    def error(self, message):

        """ Error message """

        self.log(message, severity=20)


    def fatal(self, message):

        """ Fatal message """

        self.log(message, severity=10)
