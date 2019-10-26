#!/bin/sh
rm /dev/random
ln -s /dev/urandom /dev/random
ifdown wlan0
killall -9 wpa_supplicant
ifconfig wlan0 192.168.10.1
# -B to run in background
wpa_supplicant -B -Dnl80211 -iwlan0 -c/etc/wpa_supplicant_ap.conf
udhcpd /etc/udhcpd.conf

