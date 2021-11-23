# Basic Hot tub controller
## Fred T. Dunaway
# Not ready for prime-time:  Use at your own risk!

## Project goals
1. A simple IoT controller for basic hot tub
1. Use off the shelf components

## Parts
* Raspberry Pi Zero W or equvilant
* 5V coil, contact style relays of suffient power for each power item such as motors, heaters, etc.
* Water proof DS 18B20 thermal sensor
* Water level switch/detector

## Pinout

|  Item                    | GPIO pin          | Physical pin  |
|--------------------------|-------------------|---------------|
|  Heat                    | 17                | 11            |
|  Pump low                | 27                | 13            |
|  pump_high               | 22                | 15            |
|  light                   | 23                | 16            |
|  DS18b20 VCC (3.3V)      | NA                | 1             |
|  DS18b20: SIG            | O4	               | 7             |
|  DS18b20: GND            | NA                | 9             |
|  Water level switch      | 24                | 18            |
|  Water level 5v          | NA                | 4             |
|  Water level GND         | NA                | 39            |
