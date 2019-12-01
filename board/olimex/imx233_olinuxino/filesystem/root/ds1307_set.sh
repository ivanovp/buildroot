#!/bin/sh
echo Set time to DS1307
hwclock -w -u -f /dev/rtc1

