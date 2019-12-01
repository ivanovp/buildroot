#!/bin/sh
GPIO=57
echo "Exporting $GPIO..."
echo $GPIO >/sys/class/gpio/export

echo "OUT"
echo out >/sys/class/gpio/gpio$GPIO/direction
echo "1"
echo 1 >/sys/class/gpio/gpio$GPIO/value
rmmod fb_ssd1289
rmmod fbtft_device
rmmod fbtft
rmmod fb_sys_fops
rmmod syscopyarea
rmmod sysfillrect
rmmod sysimgblt
rmmod fb
rmmod font
rmmod backlight
modprobe fbtft_device name=sainsmart32_fast rotate=1 debug=3 gpios=reset:91,cs:92,dc:52,wr:54,\
db00:32,db01:33,db02:34,db03:35,db04:36,db05:37,db06:38,db07:39,\
db08:53,db09:1,db10:2,db11:50,db12:4,db13:5,db14:6,db15:7

