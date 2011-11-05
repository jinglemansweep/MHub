import subprocess
import urllib


class Plugin(object):

    """ TTS Announcer Plugin """

    name = "announcer"
    description = "TTS announcer"
    author = "MHub"

    default_config = {
        "generator": "/opt/swift/bin/swift",
        "player": "aplay"
    }
        

    def on_init(self):

        self.tasks = []


    def on_message(self, data, message):

        """ AMQP on-message handler """

        action, params = data.get("action"), data.get("params")

        if action == "%s.action" % (self.name):

            generator = self.cfg.get("generator")
            player = self.cfg.get("player")

            message = params.get("message", "No message")

            generator_args = [
                generator,
                "-o", "/tmp/announcement.wav",
                message
            ]

            player_args = [player, "/tmp/announcement.wav"]
            
            subprocess.Popen(generator_args)
            subprocess.Popen(player_args)
            

            

        

