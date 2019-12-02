#!/bin/sh
echo Get time from DS1307
hwclock -s -u -f /dev/rtc1

