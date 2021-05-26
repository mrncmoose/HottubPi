config = {
    "GPIO" : {
        "heat": 17,
        "pump_low": 27,
        "pump_high": 22,
        "light": 10
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