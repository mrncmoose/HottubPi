import logging
import argparse
import signal
import requests
import os
import time
import re
import json
import datetime
from pytz import timezone
import pytz
from requests.auth import HTTPBasicAuth
from config import *
from maineController import Controller

class HttpBridge(object):
    
    def __init__(self, *args, **kwargs):       
        self.blogger = logging.getLogger(__name__)
        self.controller = Controller()
        self.controller.hold_temp()
        
    def removeSetPoints(self, pk=None):
        if pk != None:
            url = baseUrl + thingSetPointUri + '/{}'.format(pk)
            res = requests.delete(url, auth=HTTPBasicAuth(apiUser, apiPass), verify=True)
            if re.search(r'4\d+|5\d+', str(res.status_code)):
                raise Exception('Unable to delete setpoint data with HTTP return code of {}'.format(res.status_code))
        
    def getSetpoint(self):
        res = None
        #localTz = timezone('US/Eastern')
        utc = pytz.utc
        url = baseUrl + thingSetPointUri
        try:
            res = requests.get(url, auth=HTTPBasicAuth(apiUser, apiPass), verify=True)
            if re.search(r'4\d+|5\d+', str(res.status_code)):
                raise Exception('Unable to get setpoint data with HTTP return code of {}'.format(res.status_code))
            msg = res.json()
            if len(msg) > 0:
                for item in msg:
                    if item['name']:                     
                        if item['name'] == 'Temperature':
                            tempVal = float(item['value'])
                            try:
                                ctlWindow = float(item['controlWindow'])
                                self.controller.setTempControlWindow(ctlWindow)
                            except Exception as e:
                                self.blogger.warn('Unable to set the control window.  Using default of 1.0')
                                self.controller.setTempControlWindow(1.0)
                            self.controller.setTempSetpoint(tempVal)
                        if item['name'] == 'Light':
                            lVal = str(item['value'])
                            lightVal = lVal.casefold()
                            self.blogger.debug('Value of light: {}'.format(lightVal))
                            if lightVal == 'ON'.casefold():
                                self.controller.setLight(True)
                            else:
                                self.controller.setLight(False)
                        if item['name'] == 'Pump':
                            pVal = str(item['value']).capitalize()
                            self.controller.set_pump_level(pVal)
                        self.removeSetPoints(pk=item['id'])
        except Exception as e:
            self.blogger.error('Unable to read setpoints from server {} for reason: {}'.format(url, e))
            return False
        return True
    
    def sendData(self):
        try:
            url = baseUrl + thingDataUri
            currentTemp = self.controller.getCurrentTemp()
            d = datetime.datetime.now()
            msg = [
                    {
                    'ttReadTime': '{}'.format(d.strftime('%Y-%m-%dT:%H:%M:%M')),
                    'sensorType': sensorTypes['temperature'],
                    'dataValue': '{}'.format(currentTemp),
                    'thing': ourThingId
                },
                {
                    'ttReadTime': '{}'.format(d.strftime('%Y-%m-%dT:%H:%M:%M')),
                    'sensorType': sensorTypes['heat'],
                    'dataValue': '{}'.format(self.controller.isHeating),
                    'thing': ourThingId                    
                },
                {
                    'ttReadTime': '{}'.format(d.strftime('%Y-%m-%dT:%H:%M:%M')),
                    'sensorType': sensorTypes['two speed motor'],
                    'dataValue': '{}'.format(self.controller.pump_mode),
                    'thing': ourThingId                       
                },
                {
                    'ttReadTime': '{}'.format(d.strftime('%Y-%m-%dT:%H:%M:%M')),
                    'sensorType': sensorTypes['water_level'],
                    'dataValue': '{}'.format(self.controller.isWaterLevel),
                    'thing': ourThingId                       
                }
            ]
            res = requests.post(url, json=msg, auth=HTTPBasicAuth(apiUser, apiPass), verify=True)
            if re.search(r'4\d+|5\d+', str(res.status_code)):
                raise Exception('Unable to post thermal data to server {} with HTTP return code of {}'.format(url, res.status_code))
            return True
        except Exception as e:
            self.blogger.error('Unable to send thermal data for reason: {}'.format(e))
            
        return False
            
    def run(self, loopDelay=10):
        while True:
            time.sleep(loopDelay)
            self.getSetpoint()
            self.sendData()
            self.controller.hold_temp()

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
    maineBridge = HttpBridge()
    maineBridge.run(httpListenerLoopDelaySeconds)
