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
import threading
import signal

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

class Controller():
    def __init__(self):
        self.mode = "STANDBY"
        self.temp_sensor_path = config['temp_sensor_path']
        self.temp_cal_m = config['temp_cal_m']
        self.temp_cal_b = config['temp_cal_b']
        self.temp_setpoint = config['limits']['min_temp']
        self.temp_window = config['limits']['control_window']
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        # Set relay pins as output
        GPIO.setup(config['GPIO']['heat'], GPIO.OUT)
        GPIO.setup(config['GPIO']['pump_low'], GPIO.OUT)
        GPIO.setup(config['GPIO']['pump_high'], GPIO.OUT)
        GPIO.setup(config['GPIO']['light'], GPIO.OUT)
        #initialize to off
        GPIO.output(config['GPIO']['heat'], GPIO.LOW)
        GPIO.output(config['GPIO']['pump_low'], GPIO.LOW)
        GPIO.output(config['GPIO']['pump_high'], GPIO.LOW)
        GPIO.output(config['GPIO']['light'], GPIO.LOW)

    def getCurrentTemp(self):
        # append the device file name to get the absolute path of the sensor 
        fileobj = open(self.temp_sensor_path,'r')
        lines = fileobj.readlines()
        fileobj.close()
        myRegex = re.compile(r"=")
        crc = myRegex.split(lines[0])
        crc = crc[1][3:-1]
        tempStr = myRegex.split(lines[1])
        tempVal = round(float(tempStr[1])/1000, 1)
        tempRetVal = 30
        if "YES" in crc:
            eventLogger.info("Temperature\t " + str(tempVal))
            tempRetVal = (tempVal * self.temp_cal_m) + self.temp_cal_b
        else:
            eventLogger.warn("Got bad crc reading temperature sensor")
        return tempRetVal

    def filtering_on(self):
        if self.mode != "HEATING":
            self.mode = "FILTERING"
            self.set_pump_level('LOW')

    def filtering_off(self):
        if self.mode != "HEATING":
            self.mode = "STANDBY"
            self.set_pump_level('OFF')

    def setTempSetpoint(self, setpoint: float):
        if setpoint > config['limits']['max_temp']:
            setpoint = config['limits']['max_temp']
        if setpoint < config['limits']['min_temp']:
            setpoint = config['limits']['min_temp']
        self.temp_setpoint = setpoint

    def setTempControlWindow(self, window: float):
        self.temp_window = window

    def setLight(self, lightVal: bool):
        if lightVal:
            GPIO.output(config['GPIO']['light'], GPIO.HIGH)
        else:
            GPIO.output(config['GPIO']['light'], GPIO.LOW)

    def set_pump_level(self, level):
        if level == 'OFF':
            GPIO.output(config['GPIO']['pump_low'], GPIO.LOW)
            GPIO.output(config['GPIO']['pump_high'], GPIO.LOW)
        if level == 'HIGH':
            GPIO.output(config['GPIO']['pump_low'], GPIO.LOW)
            GPIO.output(config['GPIO']['pump_high'], GPIO.HIGH)
        if level == 'LOW':
            GPIO.output(config['GPIO']['pump_low'], GPIO.HIGH)
            GPIO.output(config['GPIO']['pump_high'], GPIO.LOW)       

    def doFiltering(self):
        now =  time.localtime()
        filterOn = config['filter_on'].split(':')
        filterOff = config['filter_off'].split(':')
        if filterOn[0] == now.tm_hour and filterOn[1] == now.tm_min:
            controller.filtering_on()
        if filterOff[0] == now.tm_hour and filterOff[1] == now.tm_min:
            controller.filtering_off()        

    def hold_temp(self):
        currentTemp = self.getCurrentTemp()
        if currentTemp > self.temp_setpoint + (self.temp_window/2):
            GPIO.output(config['GPIO']['heat'], GPIO.LOW) 
        if currentTemp <= self.temp_setpoint - (self.temp_window/2):
            GPIO.output(config['GPIO']['heat'], GPIO.HIGH)
        self.doFiltering()

##----------------- End of class

def exit_clean(signum, frame):
    print('Exiting on kill signal')
    GPIO.cleanup()
    sys.exit(0)

if __name__ == '__main__':
    signal.signal(signal.SIGTERM, exit_clean)
    signal.signal(signal.SIGABRT, exit_clean)

    parser = argparse.ArgumentParser()
    parser.add_argument("--log_level", 
                    help="The level of log messages to log", 
                    default="INFO", 
                    choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'])
    args = parser.parse_args()
    controller = Controller()

    while True:
        controller.hold_temp()
        currentTemp = controller.getCurrentTemp()
        logging.info('Current temperature: {} C'.format(currentTemp))
        time.sleep(1)
        