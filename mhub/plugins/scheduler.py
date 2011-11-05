import datetime
import random

from twisted.internet.task import LoopingCall

from base import BasePlugin


class SchedulerPlugin(BasePlugin):

    def __init__(self, name, cls, service, cfg):

        BasePlugin.__init__(self, name, cls, service, cfg)

        self.env = dict()
        self.intervals = ["year", "month", "day", "hour", "minute", "second"]
        self.schedules = dict()
        self.first_run = True

        lc = LoopingCall(self.process_schedules)
        lc.start(1.0)


    def process_intervals(self):
        
        """ Process current date and time values and changes """

        dt = datetime.datetime.now()

        publish_intervals = self.cfg.get("publish_intervals", list())

        env = self.env

        if not "datetime" in env: env["datetime"] = {}

        for interval in  self.intervals:
            current = getattr(dt, interval)
            new_interval = ((env.get("datetime").get(interval, current) != current))
            env["datetime"]["new_%s" % (interval)] = new_interval
            env["datetime"][interval] = current
            if new_interval:
                if interval in publish_intervals:
                    self.publish_event("new_interval", {
                        "interval": interval,
                        "now": [getattr(dt, i) for i in self.intervals]
                    })

        self.env = env


    def process_schedules(self):
        """ Process configured schedules """

        schedules = self.cfg.get("schedules")

        self.process_intervals()
        
        dt = self.env.get("datetime")
        ts = dt.get("timestamp")

        for name, cfg in schedules.iteritems():

            schedule = self.schedules.get(name, cfg)

            scope = schedule.get("scope", "day")

            if "actual" not in schedule:
                schedule["actual"] = dict()

        if self.first_run or dt.get("new_%s" % (scope)):

            td_dict = dict()

            for interval in self.intervals:
                value = schedule.get(interval, -1)
                if interval in ["hour", "minute", "second"] and value >= 0:
                    td_dict[interval + "s"] = value

            fuzziness = schedule.get("fuzziness", 0)
            offset = (0 - (fuzziness // 2)) + random.randint(0, fuzziness)
            td = datetime.timedelta(**td_dict)
            td = td - datetime.timedelta(minutes=offset)

            s = td.seconds
            hours = s // 3600
            s = s - (hours * 3600)
            minutes = s // 60
            seconds = s - (minutes * 60)

            actuals = {
                "hour": hours,
                "minute": minutes,
                "second": seconds
            }

            self.logger.info("Schedule '%s': %02d:%02d:%02d" % (name, hours, minutes, seconds))

            schedule["actual"] = actuals
            schedule["fired"] = False

        if dt.get("new_second"):
            
            actuals = schedule.get("actual")

            trigger_matches = 0
            trigger_total = 0

            for trigger in self.intervals:
                value = actuals.get(trigger)

                if value >= 0:
                    trigger_total += 1
                    if value == int(dt.get(trigger)):
                        trigger_matches += 1

            matched = (trigger_total > 0 and trigger_matches == trigger_total)

            if matched and not schedule.get("fired", False):
                
                schedule["fired"] = True

                self.publish_event("new_schedule", {"schedule": schedule})

        self.schedules[name] = schedule

        self.first_run = False


