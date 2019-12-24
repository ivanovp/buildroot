#!/bin/sh
if [ "$1" == "" ]; then
    echo "Usage: $0 <device>"
else
    DEV=$1
    umount ${DEV}1 ${DEV}2 ${DEV}3
    dcfldd if=output/images/sdcard.img of=$DEV
    sync
fi

