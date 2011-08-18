from twisted.application.service import ServiceMaker

service_maker = ServiceMaker("MHub", 
                             "mhub.services.twistd", 
                             "MHub Event Messaging Bus", 
                             "mhub")
