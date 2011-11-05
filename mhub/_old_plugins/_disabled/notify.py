import datetime
import fnmatch

from twisted.python import log


class Plugin(object):

    """ Notify Plugin """


    name = "notify"
    description = "Notifications (libnotify)"
    author = "MHub"

    default_config = {
        "patterns": ["twitter.*", "*.action"]
    }


    def on_message(self, data, message):

        """ On AMQP message handler """

        action, params = data.get("action"), data.get("params")

        if self.matches_patterns(action):

            title = params.get("title", "")
            message = params.get("message", "")

            try:
                import pynotify
                if pynotify.init("MHub"):
                    n = pynotify.Notification(title, message)
                    n.show()
            except:
                pass


    def on_init(self):

        """ On Init """

        self.patterns = self.cfg.get("patterns", list("*"))


    def matches_patterns(self, action):

        match = False

        for pattern in self.patterns:
            match = fnmatch.fnmatch(action, pattern)
            if match: break

        return match
