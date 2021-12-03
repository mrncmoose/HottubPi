import os
import logging

config = {
    "GPIO" : {
        "heat": 17,
        "pump_low": 27,
        "pump_high": 22,
        "light": 23,
        "water_level": 24
    },
    "limits": {
        "max_temp": 42,
        "min_temp": 5,
        "control_window": 1.0,
        "max_at_temp_hours": 1,
    },
    "filter_on": '09:30:00',
    'filter_off': '12:30:00',
    'temp_sensor_path': '/sys/bus/w1/devices/28-0118410baaff/w1_slave',
    'temp_cal_m': 1.0,
    'temp_cal_b': 0.0,
    'testMode': True
}

# Key values for Sensor types
sensorTypes = {
    'temperature': 1,
    'two speed motor': 7,
    'heat': 8,
    'water_level': 6
}

#All credentials are in environment vars
apiUser = None
apiPass = None
baseUrl = None

try:
    apiUser = os.getenv('API_USER')
    apiPass = os.getenv('API_PASSWD')
    baseUrl = os.getenv('API_BASE_URL')
except Exception as e:
    logging.fatal('Unable to find api credintails in environment.  Exiting.')
    SystemExit(1)

thingDataUri = '/iot/api/thing-data/'
thingSetPointUri = '/iot/api/thing-setpoint'
thingLoopDelay = 120        # The number of seconds for the thingy to wait in it's main processing loop
ourThingId = 4
httpListenerLoopDelaySeconds = 10
