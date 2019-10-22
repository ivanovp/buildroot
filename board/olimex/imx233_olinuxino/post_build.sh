#!/bin/sh
echo "--- iMX233-OLinuXino ---"
cp -rv board/olimex/imx233_olinuxino/etc ${TARGET_DIR}
cp -rv board/olimex/imx233_olinuxino/bt-audio ${TARGET_DIR}/root
