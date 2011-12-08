from __future__ import division
import json
import logging
import math
import urllib2
import pprint
from twisted.internet.protocol import Protocol, Factory
from twisted.internet.task import LoopingCall
from twisted.application.internet import TCPServer

from base import BasePlugin




class LatitudePlugin(BasePlugin):

    """
    Google Latitude plugin.

    :param name: Name of plugin.
    :type name: str.
    :param cls: Class/type of plugin.
    :type cls: str.
    :param service: Container service.
    :type service: mhub.service.
    :param cfg: Plugin configuration dictionary.
    :type cfg: dict.
    """

    def __init__(self, name, cls, service, cfg):

        """ Constructor """

        BasePlugin.__init__(self, name, cls, service, cfg)

        self.feeds = self.cfg.get("feeds", dict())
        self.zones = self.cfg.get("zones", dict())
        self.zone_state = dict()
        self.first_run = True

        poll_task = LoopingCall(self.poll_feeds)
        poll_task.start(self.cfg.get("poll_interval", 60))


    def poll_feeds(self):

        """ Polls Google Latitude JSON feeds """

        for name, url in self.feeds.iteritems():
            
            self.logger.debug("Polling location for: %s" % (name))
            req = urllib2.Request(url, None, {"Content-Type": "application/json"})
            f = urllib2.urlopen(req)
            res = f.read()
            f.close()
            try:
                doc = json.loads(res)
                features = doc.get("features")[0]
                geo = features.get("geometry", dict())
                props = features.get("properties", dict())
                geo_coords = geo.get("coordinates")
                geo_type = geo.get("type").lower()
                detail = {
                    "feed": name,
                    "coords": geo_coords,
                    "type": geo_type,
                    "accuracy": props.get("accuracyInMeters"),
                    "timestamp": props.get("timeStamp"),
                    "location": props.get("reverseGeocode")
                }
                self.apply_zones(name, geo_coords)
                self.publish_event("location", detail)
            except:
                continue


    def apply_zones(self, feed, latlong):

        """ Apply zone/perimeter checking """

        lng_cur, lat_cur = latlong

        for name, detail in self.zones.iteritems():

            latitude = float(detail.get("latitude", 0.0))
            longitude = float(detail.get("longitude", 0.0))
            radius = float(detail.get("radius", 1.0))

            if latitude == 0.0 and longitude == 0.0: continue

            lng_min = longitude - radius / abs(math.cos(math.radians(latitude)) * 69)
            lng_max = longitude + radius / abs(math.cos(math.radians(latitude)) * 69)
            lat_min = latitude - (radius / 69)
            lat_max = latitude + (radius / 69)

            # print radius
            # print lat_min, lat_cur, lat_max
            # print lng_min, lng_cur, lng_max
          
            if not name in self.zone_state: self.zone_state[name] = dict()
           
            cur_state = self.zone_state.get(name).get(feed, False)
            inside = ((lat_min < lat_cur < lat_max) and (lng_min < lng_cur < lng_max))
  
            changed = ((cur_state != inside) or self.first_run)
            self.zone_state[name][feed] = inside

            if changed:
                zone_detail = dict(feed=feed, zone=name, inside=inside, outside=not inside)
                self.publish_event("zone", zone_detail)

        self.first_run = False
        
        
