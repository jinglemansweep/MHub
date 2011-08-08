from twisted.application.service import ServiceMaker

service_maker = ServiceMaker("MHub", "mhub.twistedservice", "MHub Event Messaging Bus", "mhub")
