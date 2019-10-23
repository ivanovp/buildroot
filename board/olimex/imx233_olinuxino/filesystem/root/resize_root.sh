#!/bin/sh
MEDIA=/dev/mmcblk0
PART_ID=3
DEV=${MEDIA}p${PART_ID}
MEDIA_SECTORS=`fdisk -l $MEDIA|head -1|awk '{ print $7 }'`
START_SECTOR=`fdisk -l $MEDIA|grep $DEV|awk '{ print $4 }'`
LENGTH=`fdisk -l $MEDIA|grep $DEV|awk '{ print $6 }'`
PART_TYPE=`fdisk -l $MEDIA|grep $DEV|awk '{ print $8 }'`
echo Start sector: $START_SECTOR
echo Partition type: $PART_TYPE
NEW_LENGTH=$((MEDIA_SECTORS - START_SECTOR))
echo Partition length: $LENGTH
echo Maximum length of partition: $NEW_LENGTH
if [ $NEW_LENGTH -gt $LENGTH ]; then
  echo Partitioning needed
cat<<EOF |fdisk $MEDIA
d
$PART_ID
n
p
$PART_ID
$START_SECTOR

w
EOF
echo '*** Please, reboot system an re-run this script! ***'
else
  echo Resizing file system
  resize2fs $DEV
fi

