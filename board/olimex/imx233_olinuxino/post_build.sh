#!/bin/sh
echo "--- iMX233-OLinuXino ---"
cp -v board/olimex/imx233_olinuxino/interfaces ${TARGET_DIR}/etc/network/interfaces
cp -v board/olimex/imx233_olinuxino/wpa_supplicant.conf ${TARGET_DIR}/etc/wpa_supplicant.conf
cp -rv board/olimex/imx233_olinuxino/bt-audio ${TARGET_DIR}/root
