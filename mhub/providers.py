from pysqueezecenter.server import Server



class SqueezeboxServerProvider(object):

    ACTION_MAP = {
        "play": "play",
        "stop": "stop",
        "pause": "pause",
        "unpause": "unpause",
        "toggle": "toggle",
        "next": "next",
        "previous": "prev",
        "volume_up": "volume_up",
        "volume_down": "volume_down"
        
    }

    def __init__(self, host="localhost", port=9090, username=None, password=None):

        self.host = host
        self.port = port
        self.username = username
        self.password = password
        
        self.players = dict()

        self.connect()

    def connect(self):

        sc = Server(hostname=self.host, port=self.port, username=self.username, password=self.password)
        sc.connect()

        for player in sc.get_players():
            self.players[player.name] = player




    def message_received(self, message_data, message):

        cmd = message_data.get("cmd", "").lower()
        params = message_data.get("params", None)
        print cmd
        map_cmd = self.ACTION_MAP.get(cmd.lower(), None)
        print map_cmd

        if map_cmd is not None:
            for name, player in self.players.iteritems():
                if hasattr(player, map_cmd):
                    cb = getattr(player, map_cmd)
                    print name + ": " + map_cmd
                    if params is not None:
                        try:
                            cb(**params)
                        except:
                            print "Invalid parameters"
                    else:
                        cb()

                
    def cmd_play(self, params=None):
        print "Play"


class MPDProvider(object):

    def __init__(self, host="localhost", port=6600, username=None, password=None):

        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.players = {"main": {}}


class XBMCProvider(object):

    def __init__(self, host="localhost", port=6600, username=None, password=None):

        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.players = {"main": {}}
