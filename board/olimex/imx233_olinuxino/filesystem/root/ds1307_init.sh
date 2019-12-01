#!/bin/sh
echo Initialize DS1307
modprobe rtc-ds1307
echo ds1307 0x68 > /sys/class/i2c-dev/i2c-0/device/new_device

