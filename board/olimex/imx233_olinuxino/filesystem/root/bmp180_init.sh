#!/bin/sh
modprobe i2c-dev
echo Check if device with ID 0x77 exists
i2cdetect -y -r 0
echo Installing kernel module for BMP170
modprobe bmp280_i2c
#echo bmp085 0x77 > /sys/bus/i2c/devices/i2c-0/new_device
echo bmp180 0x77 > /sys/bus/i2c/devices/i2c-0/new_device
#cat /sys/bus/i2c/devices/0-0077/name
echo Set oversampling for pressure measurement...
echo 8 >/sys/bus/iio/devices/iio:device1/in_pressure_oversampling_ratio
echo Pressure:
cat /sys/bus/iio/devices/iio:device1/in_pressure_input
echo Temperature:
cat /sys/bus/iio/devices/iio:device1/in_temp_input

