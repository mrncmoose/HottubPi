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

class HttpBridge(object):
    
    def __init__(self, *args, **kwargs):       
        self.blogger = logging.getLogger(__name__)
        
    def getSetpoint(self):
        res = None
        #localTz = timezone('US/Eastern')
        utc = pytz.utc
        try:
            url = baseUrl + thingSetPointUri
            res = requests.get(url, auth=HTTPBasicAuth(apiUser, apiPass), verify=True)
            if re.search(r'4\d+|5\d+', str(res.status_code)):
                raise Exception('Unable to get temperature from controller with HTTP return code of {}'.format(res.status_code))
            
        except Exception as e:
            self.blogger.error('Unable to read setpoints from server {} for reason: {}'.format(url, e))
            return False
        #TODO Update to process the setpoints, including deleting them from the server.
        try:
            url = centralServer['baseURL'] + centralServer['currentReadingURI']
            tempMes = res.json()
            d = datetime.datetime.now(utc)
            thingOwner = os.environ['THING_OWNER']
            thingPass = os.environ['THING_PASSWORD']
            reading = {
                    'ttReadTime': '{}'.format(d.strftime('%Y-%m-%dT%H:%M:%SZ')),
                    'sensorType': 1,
                   'dataValue': '{}'.format(tempMes['current_temp']),
                   'thing': ourThingId
                }
            mes = json.dumps(reading)
            res = requests.post(url, json=reading, auth=HTTPBasicAuth(thingOwner, thingPass), verify=True)
            self.blogger.debug('Post current reading status code: {0}\n for message: {1}\nTo URL: {2}'.format(res.status_code, mes, url))
            if re.search(r'4\d+|5\d+', str(res.status_code)):
                raise Exception('Unable to send data to central server with HTTP return code of {}'.format(res.status_code))

        except Exception as e:
            self.blogger.error('Unable to put readings to central server for reason: {}'.format(e))
            return False
        self.blogger.debug('Successfully posted device reading to central server.') 
        return True
    
    def getEvents(self):
        try:
            url = centralServer['baseURL'] + centralServer['eventURI']
            isEventInPast = False
            res = requests.get(url, auth=HTTPBasicAuth(os.environ['THING_OWNER'], os.environ['THING_PASSWORD']), verify=True)
            if re.search(r'4\d+|5\d+', str(res.status_code)):
                raise Exception('Unable to get events from central server with HTTP return code of {}'.format(res.status_code))
            events = res.json()
            self.blogger.debug('Got events from central server: {}'.format(events))
            if len(events) > 0:
                url = baseURL + eventURI
                localEvents = []
                for ev in events:
                    now = datetime.datetime.now()
                    setDate = datetime.datetime.strptime(ev['on_when'], "%Y-%m-%dT%H:%M:%SZ")
                    if setDate >= now:
                        lEv = {'on':{
                                  'motion_delay_seconds':ev['on_motion_delay_seconds'],
                                  'when': ev['on_when'],
                                  'temperature': ev['on_temperature']                              
                                  },
                                 'off': {'temperature': ev['off_temperature']}
                            }
                        localEvents.append(lEv)
                    else:
                        self.blogger.info('Set point datetime is in the past.')
                        isEventInPast = True
                if not isEventInPast:
                    jsonMess = json.dumps(localEvents)
                    resp = requests.post(url, json=jsonMess, auth=HTTPBasicAuth(localApiUser, localApiPass), verify=True)
                    if re.search(r'4\d+|5\d+', str(resp.status_code)):
                        raise Exception('Unable to send event to local server.  HTTP return code: {}'.format(resp.status_code))
                return True
            else:
                self.blogger.debug('No events fetched from central server at URL: {}'.format(url))
        except Exception as e:
            self.blogger.error('Unable to send event for reason: {}'.format(e))
            
        return False
            
    def run(self, loopDelay=600):
        while True:
            time.sleep(loopDelay)
            self.getEvents()
            self.putReadings()
    