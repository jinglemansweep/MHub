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

	for p, t in self.sensors.iteritems():
	   sensor = ow.Sensor(p)
	   if hasattr(sensor, "temperature"):
               temperature = float(sensor.temperature)
	       self.sensors[p]["temperature"] = temperature
	   if hasattr(sensor, "humidity"):
               humidity = float(sensor.humidity)
               self.sensors[p]["humidity"] = humidity
           if hasattr(sensor, "vis"):
               light = float(sensor.vis)
               self.sensors[p]["light"] = light

	self.publish(["o:status"], self.sensors)


    def walk_sensor_tree(self, sensor):

	"""
	Walk sensor tree.
	"""

	if sensor._path not in self.sensors:
	    self.sensors[sensor._path] = dict(type=sensor._type)

    	for next in sensor.sensors():
            if next._type in ["DS2409"]:
                self.walk_sensor_tree(next)
            else:
		if next._path not in self.sensors: 
                    self.sensors[next._path] = dict(type=next._type)






