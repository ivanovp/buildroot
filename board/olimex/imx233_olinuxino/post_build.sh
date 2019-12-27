#!/bin/sh
echo "--- iMX233-OLinuXino ---"
rm -f ${TARGET_DIR}/etc/sudoers
cp -rv board/olimex/imx233_olinuxino/filesystem/* ${TARGET_DIR}
chmod 440 ${TARGET_DIR}/etc/sudoers
chmod o+w ${TARGET_DIR}/etc/wpa_supplicant.conf
#chgrp ftp ${TARGET_DIR}/var/lib/mpd/music
#chmod g+w ${TARGET_DIR}/var/lib/mpd/music
FTPUSER=`grep ftp ${TARGET_DIR}/etc/passwd`
if [ "$FTPUSER" == "" ]; then
    echo "--------------------> adding user"
    echo "ftp:x:900:900:Anonymous FTP User,,,:/var/lib/mpd/music:/bin/false" >>${TARGET_DIR}/etc/passwd
else
    echo "--------------------> user already added"
fi
FTPGRP=`grep ftp ${TARGET_DIR}/etc/group`
if [ "$FTPGRP" == "" ]; then
    echo "--------------------> adding group"
    echo "ftp:x:900:ftp" >>${TARGET_DIR}/etc/group
else
    echo "--------------------> group already added"
fi
