#!/bin/sh
rm /dev/random
ln -s /dev/urandom /dev/random
# -B to run in background
wpa_supplicant -Dnl80211 -iwlan0 -c/etc/wpa_supplicant_ap.conf

