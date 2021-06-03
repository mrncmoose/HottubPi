# In loop, call IoT catalog for instructions
#import http.client
import logging
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
        
    def removeSetPoints(self):

        
    def getSetpoint(self):
        res = None
        #localTz = timezone('US/Eastern')
        utc = pytz.utc
        try:
            url = baseUrl + thingSetPointUri
            res = requests.get(url, auth=HTTPBasicAuth(apiUser, apiPass), verify=True)
            if re.search(r'4\d+|5\d+', str(res.status_code)):
                raise Exception('Unable to get setpoint data with HTTP return code of {}'.format(res.status_code))
            msg = res.json()
            if len(msg) > 0:
                for item in msg:
                    if item['name']:                     
                        if item['name'] == 'Temperature':
                            tempVal = float(item['value'])
                            self.controller.setTempSetpoint(tempVal)
                        if item['name'] == 'Light':
                            lVal = str(item['value'])
                            if lVal == 'On':
                                self.controller.setLight(True)
                            else:
                                self.controller.setLight(False)
                        if item['name'] == 'Pump':
                            pVal = str(item['value'])
                            self.controller.set_pump_level(pVal.capitalize)
        except Exception as e:
            self.blogger.error('Unable to read setpoints from server {} for reason: {}'.format(url, e))
            return False
        return True
    
    def sendData(self):
        try:
            url = baseUrl + thingDataUri
            currentTemp = self.controller.getCurrentTemp()
            d = datetime.datetime.now()
            msg = {
                'ttReadTime': '{}'.format(d.strftime('%Y-%m-%dT:%H:%M:%M')),
                'sensorType': 1,
                'dataValue': '{}'.format(currentTemp),
                'thing': ourThingId
            }
            res = requests.post(url, json=msg, auth=HTTPBasicAuth(os.environ['THING_OWNER'], os.environ['THING_PASSWORD']), verify=True)
            if re.search(r'4\d+|5\d+', str(res.status_code)):
                raise Exception('Unable to post thermal data to server {} with HTTP return code of {}'.format(url, res.status_code))
            return True
        except Exception as e:
            self.blogger.error('Unable to send event for reason: {}'.format(e))
            
        return False
            
    def run(self, loopDelay=600):
        while True:
            time.sleep(loopDelay)
            self.getSetpoint()
            self.putReadings()
            self.controller.hold_temp()
    