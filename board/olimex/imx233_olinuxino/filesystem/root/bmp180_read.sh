#!/bin/sh
echo Pressure:
cat /sys/bus/iio/devices/iio:device1/in_pressure_input
echo Temperature:
cat /sys/bus/iio/devices/iio:device1/in_temp_input

