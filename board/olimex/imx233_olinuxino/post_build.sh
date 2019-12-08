#!/bin/sh
echo "--- iMX233-OLinuXino ---"
rm -f ${TARGET_DIR}/etc/sudoers
cp -rv board/olimex/imx233_olinuxino/filesystem/* ${TARGET_DIR}
chmod 440 ${TARGET_DIR}/etc/sudoers
chmod o+w ${TARGET_DIR}/etc/wpa_supplicant.conf

