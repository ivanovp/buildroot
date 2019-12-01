#!/bin/sh
echo Get time from DS1307
hwclock -r -u -f /dev/rtc1

