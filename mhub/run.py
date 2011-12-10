"""

MHub Twisted Application Container Module

.. module:: run
   :platform: Unix
   :synopsis: MHub Twisted application containment and initialisation code

.. moduleauthor:: JingleManSweep <jinglemansweep@gmail.com>

"""

import logging
from twisted.python import log


from app import MHubApp
from utils import get_configuration

#observer = log.PythonLoggingObserver()
#observer.start()

# Configuration

cfg = get_configuration()
app_id = cfg.get("app").get("general").get("app_id", "mhub")
verbose = cfg.get("app").get("general").get("verbose", True)

# Logging

log_format = "%(asctime)15s %(levelname)s [%(module)s.%(name)s] %(message)s"
log_level = logging.DEBUG if verbose else logging.INFO
logging.basicConfig(format=log_format, level=log_level)
logging.getLogger("cli").setLevel(log_level)
logging.getLogger("app").setLevel(log_level)
logging.getLogger("service").setLevel(log_level)
logging.getLogger("plugin").setLevel(log_level)
logger = logging.getLogger("cli")

# Services

container = MHubApp(cfg)
application = container.get_application()
