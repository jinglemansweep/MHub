#!/usr/bin/env python

""" mHub Command Line Client """

__revision__ = "$Id$"
__docformat__ = 'restructuredtext en'

import os
import sys
import logging
import optparse

from mhub.controllers import MainController

# Globals

project_id = "mhub-client"
project_name = "mHub Command Line Client"
project_desc = ""
project_version = "0.10"
__docformat__ = "restructuredtext en"

logger = logging.getLogger(__name__)
LOG_HELP = ','.join(["%d=%s" % (4-x, logging.getLevelName((x+1)*10)) for x in xrange(5)])
LOG_FORMAT_CONS = '%(levelname)s: %(message)s'
LOG_FORMAT_FILE = '%(asctime)s %(name)s[%(process)d] %(levelname)10s %(message)s'
LOGLEVEL_DICT = { 1 : 50, 2:40, 3:20, 4:10, 5:1 }
DEFAULT_VERBOSITY = 3

# Option Parsing

parser = optparse.OptionParser(usage="%prog or type %prog -h (--help) for help", description=__doc__, version=project_name + " v" + project_version)

parser.add_option("-v", action="count", dest="verbosity", default=DEFAULT_VERBOSITY, 
                  help="Verbosity. Add more -v to be more verbose (%s) [default: %%default]" % LOG_HELP)

parser.add_option("-l", "--logfile", dest="logfile", default=None, 
                  help="Log to file instead of console" )

parser.add_option("-k", "--key", dest="key", default="default", 
                  help="Plugin or provider key [default: %default]")

parser.add_option("-d", "--device", dest="device", default="default", 
                  help="Device to target [default: %default]")

parser.add_option("-c", "--command", dest="command", default="default", 
                  help="Command to send [default: %default]")

(options, args) = parser.parse_args()
    
# Logging Setup

verbosity = LOGLEVEL_DICT.get(int(options.verbosity), DEFAULT_VERBOSITY)

if options.logfile is None:
    logging.basicConfig(level=verbosity, format=LOG_FORMAT_CONS)
else:
    logfilename = os.path.normpath(options.logfile)
    logging.basicConfig(level=verbosity, format=LOG_FORMAT_FILE, filename=logfilename, filemode='a')
    print >> sys.stderr, "Logging to %s" % logfilename

# Main Execution

routing_key = "input.%s" % (options.key)
device = options.device
command = options.command

controller = MainController({})
controller.send_message({"device": device, "cmd": command}, key=routing_key)
