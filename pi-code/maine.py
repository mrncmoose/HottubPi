 #!/usr/bin/env python

import os
import sys
import time
import datetime
from time import sleep, strftime
import re
import json
import RPi.GPIO as GPIO
import argparse
import logging
import logging.handlers

from config import config

parser = argparse.ArgumentParser()
parser.add_argument("--log_level", 
                    help="The level of log messages to log", 
                    default="INFO", 
                    choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'])
args = parser.parse_args()
print('Arg passed in: {0}'.format(args.log_level))

# load the kernel modules needed to handle the sensor
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')
LOG_FILENAME = 'themeralController.log'
eventLogger = logging.getLogger('EventLogger')
eventLogger.setLevel(level = args.log_level)
logFormatter = logging.Formatter('%(levelname)s\t%(asctime)s\t%(message)s')
logHandler = logging.handlers.RotatingFileHandler(LOG_FILENAME, maxBytes=20000000, backupCount=2 )
logHandler.setFormatter(logFormatter)
eventLogger.addHandler(logHandler)
startTime = datetime.datetime.now()