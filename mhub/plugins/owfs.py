import logging
from twisted.internet import defer, task
from twisted.internet.task import LoopingCall

from base import BasePlugin
from lib import ow

class OwfsPlugin(BasePlugin):

    """
    OWFS (1-wire filesystem) plugin.
    """

    default_config = {
        "device": "u",
        "poll_interval": 10
    }
    

    def setup(self, cfg):

        BasePlugin.setup(self, cfg)
        
        self.device = self.cfg.get("device", "u")
        self.sensors = dict()

        ow.init(self.device)

        poll_task = LoopingCall(self.poll_bus)
        poll_task.start(self.cfg.get("poll_interval", 60))



    def poll_bus(self):
        
        """
        Retrieves sensor data from configured 1-wire bus.
        """

        self.walk_sensor_tree(ow.Sensor("/"))

        path = self.cfg.get("path", "/")
        measurements = self.cfg.get("measurements", ["temperature", "humidity", "vis"])

        results = dict()
        sensor = ow.Sensor(path)

        if sensor is None: return

        for m in measurements:
            if hasattr(sensor, m):
                result = getattr(sensor, m)
                try:
                    results[m] = float(result)
                except:
                    results[m] = None

        self.publish(["o:status"], results)


    def walk_sensor_tree(self, sensor):

	"""
	Walk sensor tree.
	"""

	if sensor._path not in self.sensors:
	    self.sensors[sensor._path] = dict(type=sensor._type)
        print sensor._path
    	for next in sensor.sensors():
            if next._type in ["DS2409"]:
                self.walk_sensor_tree(next)
            else:
		if next._path not in self.sensors: 
                    self.sensors[next._path] = dict(type=next._type)






