import os
import logging

config = {
    "GPIO" : {
        "heat": 17,
        "pump_low": 27,
        "pump_high": 22,
        "light": 23
    },
    "limits": {
        "max_temp": 30,
        "min_temp": 5,
        "max_at_temp_hours": 1,
    },
    "filter_on": '09:30:00',
    'filter_off': '12:30:00',
    'temp_sensor_path': ' /sys/bus/w1/devices/28-0118410baaff/w1_slave',
    'temp_cal_m': 1.0,
    'temp_cal_b': 0.0,
}

#All credentials are in environment vars
apiUser = None
apiPass = None
baseUrl = None

try:
    apiUser = os.getenv('API_USER')
    apiPass = os.getenv('API_PASSWD')
    baseURL = os.getenv('API_BASE_URL')
except Exception as e:
    logging.fatal('Unable to find api credintails in environment.  Exiting.')
    SystemExit(1)

tempertureURI = '/thermal/api/v1.0/current_temp'
eventURI = '/thermal/api/v1.0/events'
runningURI = '/thermal/api/v1.0/isFurnaceOn'

#The server the 'world' will interact with via it's API's.
#Polling isn't the best way to do this, but HTTP is currently the only protocol working.
centralServer = { 'baseURL': 'https://iotsmartcontroller.appspot.com',
                 'eventURI': '/iot/api/thermal-events/',
                 'currentReadingURI': '/iot/api/thing-data/',
                 'thingsURI': '/iot/api/things/'
                 }
# centralServer = { 'baseURL': 'http://10.0.0.9:8000',
#                  'eventURI': '/iot/api/thermal-events/',
#                  'currentReadingURI': '/iot/api/thing-data/',
#                  'thingsURI': '/iot/api/things/'
#                  }