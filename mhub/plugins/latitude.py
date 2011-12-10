from __future__ import division
import json
import logging
import math
import urllib2
import pprint
from twisted.internet.protocol import Protocol, Factory
from twisted.internet.task import LoopingCall
from twisted.application.internet import TCPServer
from twisted.web.client import getPage

from base import BasePlugin




class LatitudePlugin(BasePlugin):

    """
    Google Latitude plugin.
    """

    default_config = {
        "enabled": False,
        "feed": "http://latitude.json.feed",
        "zones": {
            "london": {
                "latitude": 0.0,
                "longitude": 0.0,
                "radius": 10,
                "change_only": True,
                "locations": []
            }
        }

    }

    def setup(self, cfg):

        BasePlugin.setup(self, cfg)

        self.feed = self.cfg.get("feed", None)
        self.zones = self.cfg.get("zones", dict())
        self.zone_state = dict()
        self.first_run = True

        if self.feed is None:
            self.logger.warn("No feed configured")
            return

        poll_task = LoopingCall(self.poll_feed)
        poll_task.start(self.cfg.get("poll_interval", 60))

    

    def poll_feed(self):

        getPage(self.feed).addCallbacks(callback=self.process_response,
                                        errback=self.error_response)


    def error_response(self, detail):

        self.logger.debug("Cannot poll Latitude server: %s" % (detail))


    def process_response(self, value):

        """ Polls Google Latitude JSON feeds """

        try:
            doc = json.loads(value)
            features = doc.get("features")[0]
            geo = features.get("geometry", dict())
            props = features.get("properties", dict())
            location = props.get("reverseGeocode", "")
            accuracy = props.get("accuracyInMeters", 0)
            timestamp = props.get("timeStamp")
            geo_coords = geo.get("coordinates")
            geo_type = geo.get("type").lower()
            detail = {
                "coords": geo_coords,
                "type": geo_type,
                "accuracy": accuracy,
                "timestamp": timestamp,
                "location": location
            }
            self.apply_zones(geo_coords, location)
            self.publish_event("location", detail)
        except Exception, e:
            self.logger.debug("Cannot parse Latitude response")


    def apply_zones(self, geo_coords, location):

        """ Apply zone/perimeter checking """

        lng_cur, lat_cur = geo_coords

        for name, detail in self.zones.iteritems():

            latitude = float(detail.get("latitude", 0.0))
            longitude = float(detail.get("longitude", 0.0))
            radius = float(detail.get("radius", 1.0))
            locations = detail.get("locations", list())
            change_only = detail.get("change_only", True)
            zone_type = ""

            state = self.zone_state.get(name, False)

            if radius > 0 and (latitude != 0.0 or longitude != 0.0):

                zone_type = "latitude_longitude"
                lng_min = longitude - radius / abs(math.cos(math.radians(latitude)) * 69)
                lng_max = longitude + radius / abs(math.cos(math.radians(latitude)) * 69)
                lat_min = latitude - (radius / 69)
                lat_max = latitude + (radius / 69)

                inside = ((lat_min < lat_cur < lat_max) and (lng_min < lng_cur < lng_max))
 
            elif len(locations):

                zone_type = "reverse_geocode"
                inside = False
                
                for loc in locations:
                    if loc.lower() in location.lower():
                        inside = True

            changed = ((state != inside) or self.first_run)
            self.zone_state[name] = inside

            if changed or not change_only:
                zone_detail = dict(zone=name, 
                                   zone_type=zone_type,
                                   inside=inside,
                                   outside=not inside,
                                   changed=changed)
                self.publish_event("zone", zone_detail)

            self.first_run = False
        
        
