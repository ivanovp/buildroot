#!/bin/sh
modprobe fbtft_device name=nokia3310 rotate=0 debug=3 gpios=reset:34,dc:33 busnum=1
