#!/usr/bin/env python2
# Menu for internet radio
#
# Code starts: 2019-10-23 13:30:57
# Last modify: 2019-12-08 12:21:00 ivanovp {Time-stamp}

import mpd
import time
import sys
import os
import sys
import getopt
import re
#import array
import serial
import subprocess

LAST_UPDATE_STR = "Last update: 2019-12-08 12:21:00 ivanovp {Time-stamp}"

if sys.hexversion >= 0x3000000:
    print "Python interpreter 2.x is needed."
    sys.exit (3)

class MenuControl:
    SERIAL_TIMEOUT_SEC = 1
    SERIAL_PORT = "/dev/ttyAPP0"
#    SERIAL_BAUD_RATE = 115200
    SERIAL_BAUD_RATE = 9600
    # Commands for LCD
    CMD_ECHO_DISABLE                    = "E0"
    CMD_ECHO_ENABLE                     = "E1"

    # Answer to command
    ANSWER_OK                           = 0x55
    ANSWER_ERROR                        = 0x5A
    NO_ANSWER                           = 0xAA

    FONT_SMALL          = 0x00
    FONT_WIDE           = 0x01
    FONT_MEDIUM_NUMBERS = 0x02
    FONT_BIG_NUMBERS    = 0x03
    FONT_NORMAL_NUMBERS = 0x04

    CODESET = 'iso-8859-2'
    #CODESET = 'utf-8'

    KEY_STOP    = 2
    KEY_PREV    = 4
    KEY_MENU    = 8
    KEY_PLAY    = 64
    KEY_NEXT    = 128

    def __init__ (self, port=SERIAL_PORT, serial_=None, debugLevel=10):
        self.debugLevel = debugLevel
        if self.debugLevel >= 10:
            print "Menu.__init__"
        self.high = False
        self.serial = serial_
        if self.serial is None:
            if self.debugLevel >= 10:
                print "Opening serial port %s... " % (self.SERIAL_PORT),
            try:
                self.serial = serial.Serial (port, self.SERIAL_BAUD_RATE, serial.EIGHTBITS, serial.PARITY_NONE, serial.STOPBITS_ONE, self.SERIAL_TIMEOUT_SEC)
                #print "Serial:", self.serial
                #self.serial.open ()
                #self.serial.read (32) # Read header "Compiled on 2011 blah-blah"
            except serial.serialutil.SerialException, errStr:
                print ""
                print "Error:", errStr
            else:
                if self.debugLevel >= 10:
                    print "Ok."
        else:
            # TODO exception handling
            self.serial.open ()
        print "Reading all data from serial line"
        self.sendCommand (self.CMD_ECHO_DISABLE)
        while (self.serial.read (1) != ""):
            pass
#        print "Waiting for menu"
#        while (self.sendCommand (self.CMD_ECHO_DISABLE) != self.ANSWER_OK):
#            time.sleep (0.1)
        print "Initialized"

    def __del__ (self):
        if self.debugLevel >= 10:
            print "Menu.__del__"
        if self.serial is not None and self.serial.isOpen ():
            if self.debugLevel >= 10:
                print "Closing serial port..."
            self.serial.close ()
  
    # Transmit command and parameter and receives answer.
    # @param command 8-bit command
    # @return Answer is self.ANSWER_OK if executing of command was successful. Answer is self.ANSWER_ERROR if error occurred.
    def sendCommand (self, command):
        answer = 0
        if self.serial is not None and self.serial.isOpen ():
            cmd = command
            #cmd = command.encode(self.CODESET)
            #print "\r\n[%s]\r\n" % cmd
            self.serial.write (cmd + "\n")
            time.sleep (0.001)
            r = self.serial.read (1)
            if r != "":
                answer |= ord (r)
#               print "answer: 0x%02X (%c)" % (answer, chr (answer))
            else:
                answer |= self.NO_ANSWER
        else:
            # TODO throw exception
            if self.debugLevel >= 5:
                print "Menu.sendCommand: serial port is not opened!"
        if self.debugLevel >= 10:
            if answer == self.ANSWER_OK:
                answerStr = "Ok"
            elif answer == self.ANSWER_ERROR:
                answerStr = "Error"
            else:
                answerStr = "Unknown"
            print "Answer: 0x%02X %s" % (answer, answerStr)
        return answer == self.ANSWER_OK

    def clearScreen(self):
        return self.sendCommand("C")
    
    def setFont(self, font=FONT_SMALL):
        return self.sendCommand("F%i" % font)

    def printStr(self, x, y, string):
        cmd = "P%03i,%03i,%s" % (x, y, string)
        return self.sendCommand(cmd)

    def setVolume(self, volume):
        cmd = "V%03i" % volume
        return self.sendCommand(cmd)

    def getVolume(self):
        cmd = "G"
	vol = None
        volChanged = None
        if self.sendCommand(cmd):
            vol = int(self.serial.read(3))
            volChanged = self.serial.read(1) == "!"
            self.serial.read(2) # CR, LF
	return [vol, volChanged]

    def getKey(self):
        cmd = "K"
	key = None
        if self.sendCommand(cmd):
            key = int(self.serial.read(3))
            self.serial.read(2) # CR, LF
	return key

    def showMenu(self, *argv):
        if self.setFont(self.FONT_SMALL):
            cmd = "M"
            width = 19
            for arg in argv: 
                if len (arg) < width:
                    arg += " " * (width - len (arg))
                cmd += arg + "|"
            return self.sendCommand(cmd)
        else:
            return False

    def getActivatedMenu(self):
        cmd = "Y"
	activatedMenu = None
        if self.sendCommand(cmd):
            activatedMenu = int(self.serial.read(3))
            self.serial.read(2) # CR, LF
	return activatedMenu
    
class App:
    VERSION_STR = "1.0.0"
    AUTHOR_STR = "Peter Ivanov <ivanovp@gmail.com>"
    DEFAULT_SERIAL_PORT = "/dev/ttyAPP0"

    def __init__ (self):
        self.verboseLevel = 5
        self.serialPort = self.DEFAULT_SERIAL_PORT
	self.enablePrint = True

        # Processing remaining switches
        try:
            opts, args = getopt.getopt(sys.argv[1:], "p:hv:", ["port=", "help", "verbose="])
        except getopt.GetoptError, err:
            # print help information and exit:
            print "Error:", str (err) # will print something like "option -a not recognized"
            print ""
            self.usage ()
            sys.exit (2)
        for o, a in opts:
            if o in ("-v", "--verbose"):
                self.verboseLevel = int (a)
            elif o in ("-h", "--help"):
                self.usage ()
                sys.exit ()
            elif o in ("-p", "--port"):
                self.serialPort = a
            else:
                assert False, "unhandled option"

        if self.verboseLevel >= 3:
            print self.getProgHeader ()

        # use_unicode will enable the utf-8 mode for python2
        # see https://python-mpd2.readthedocs.io/en/latest/topics/advanced.html#unicode-handling
        self.mpdclient = mpd.MPDClient(use_unicode=False)
        #self.mpdclient = mpd.MPDClient(use_unicode=True)
        self.mpdclient.connect("localhost", 6600)

        if self.verboseLevel >= 10:
            print
            print "Serial port:", self.serialPort
            print "Verbose level:", self.verboseLevel

    def getProgHeader (self):
        header = "menu v%s - LCD menu\n" % self.VERSION_STR
        header += "Copyright (C) %s\n" % self.AUTHOR_STR
        header += LAST_UPDATE_STR
        return header

    def usage (self):
        prg = sys.argv[0]
        print self.getProgHeader (), "\n"
        print prg, " [-p </dev/ttyAPP0>] [-h] [-v <verbose_level>]"
        print """
Switches:
  -p: Set serial port device. Default: %s
  -h: Print this help.
  -v: Set verbose level. Range: 0..20
""" % (self.DEFAULT_SERIAL_PORT)

#import stat
#import os.stat
#    def disk_exists(self,path):
#        try:
#            return stat.S_ISBLK(os.stat(path).st_mode)
#        except:
#            return False

    def disk_exists(self,path):
        return os.path.exists(path)

    def mount (self, path):
        print "mounting %s" % path,
        if not os.path.exists("/var/lib/mpd/music/mst"):
            os.mkdir("/var/lib/mpd/music/mst")
        ret = not os.system("mount -t vfat -o ro %s /var/lib/mpd/music/mst" % path)
        if ret:
            print "OK"
        else:
            print "Error!"
        return ret

    def umount (self):
#        # automatically unmounted when removing
#        return True
        print "unmounting",
        ret = os.system("umount /var/lib/mpd/music/mst")
        if ret:
            print "OK"
        else:
            print "Error!"
        return ret

    def printDisk(self, disk):
        self.menu.setFont(self.menu.FONT_SMALL)
        if disk:
            status = "U"
        else:
            status = "."
        self.menu.printStr(112, 55, status)
    
    def printLink(self, link):
        self.menu.setFont(self.menu.FONT_SMALL)
        if link:
            status = "L"
        else:
            status = "."
        self.menu.printStr(120, 55, status)

    def runCommand(self, command):
        return subprocess.check_output(command.split(" "))

    def updateDisk(self, disk):
        if self.disk_exists("/dev/sda1"):
            if not disk:
                self.mount("/dev/sda1")
                disk = True
        elif self.disk_exists("/dev/sda"):
            if not disk:
                #disk = self.mount("/dev/sda")
                self.mount("/dev/sda")
                disk = True
        elif disk:
            # disk removed
            #disk = self.umount()
            self.umount()
            disk = False
        return disk

    def updateLink(self):
        link = False
        output = self.runCommand("ip addr show wlan0")
        m = re.search(r"inet (\S+)", output)
        if m:
            #ip = m.group(1)
            link = True
        return link

    def run (self):
        self.menu = MenuControl (self.serialPort, None, self.verboseLevel)
        self.menu.clearScreen()
        if self.verboseLevel >= 15:
            print "--- lsinfo ---"
            for entry in self.mpdclient.lsinfo("/"):
                print("%s" % entry)
            print "--- status ---"
            for key, value in self.mpdclient.status().items():
                print("%s: %s" % (key, value))
            print "--- stats ---"
            print self.mpdclient.stats()
            print "--- currentsong ---"
            print self.mpdclient.currentsong()
            print "--- playlist --"
            print self.mpdclient.playlist()
            print "--- playlistid --"
            print self.mpdclient.playlistid()
            print "--- playlistinfo --"
            print self.mpdclient.playlistinfo()
            print "--- urlhandlers --"
            print self.mpdclient.urlhandlers()
            print "--- decoders --"
            print self.mpdclient.decoders()

        name = ""
        title = ""
        filename = ""
        timeTxt = ""
        prevTimeTxt = ""
        titleTxt = ""
        prevTitleTxt = ""
        state = ""
        mpdvolume = 0
        status = self.mpdclient.status()
        if 'volume' in status:
            self.menu.setVolume(int(status['volume']))
            mpdvolume = status['volume']
	(volume, volumeChanged) = self.menu.getVolume()
	font = -1
	prevFont = -1
        disk = False
        prevDisk = False
        prevLink = False
        menuState = 0
        forcePrintTitle = True
        forcePrintTime = True
        forcePrintStatus = True
        forcePrintDisk = True
        forcePrintLink = True
        while True:
            #self.mpdclient.idle()
            end = False
            #while not end:
            #    vol = self.menu.serial.read(4)
            #    if len(vol) > 0 and vol[0] == 'V':
            #        print "\nvolume", vol
            #    else:
            #        end = True
            time.sleep(0.1)
#            try:
            song = self.mpdclient.currentsong()
            status = self.mpdclient.status()
#            except UnicodeDecodeError as err:
#                print "Unicode error:", err
            disk = self.updateDisk(disk)
            link = self.updateLink()
            key = self.menu.getKey()
            if key != 0:
                print "\r\nkey:", key
                if key & self.menu.KEY_PREV:
                    if status['state'] == 'play':
                        print "prev"
                        self.mpdclient.previous()
                    else:
                        print "play"
                        self.mpdclient.play()
                if key & self.menu.KEY_NEXT:
                    if status['state'] == 'play':
                        print "next"
                        self.mpdclient.next()
                    else:
                        print "play"
                        self.mpdclient.play()
                if key & self.menu.KEY_PLAY:
                    if status['state'] == 'play':
                        print "pause"
                        self.mpdclient.pause()
                    else:
                        print "play"
                        self.mpdclient.play()
                if menuState == 0 and key & self.menu.KEY_MENU:
                    choose = self.menu.showMenu("Seek", "Power off", "Show IP", "WiFi AP mode", "Back")
                    menuState = 1
            if 'elapsed' in status:
                elapsed_min = float (status['elapsed']) / 60
                elapsed_sec = float (status['elapsed']) % 60
            else:
                elapsed_min = 0
                elapsed_sec = 0
            if 'duration' in status:
                duration_min = float (status['duration']) / 60
                duration_sec = float (status['duration']) % 60
                timeTxt = "%i:%02i/%i:%02i" % (elapsed_min, elapsed_sec, duration_min, duration_sec)
            else:
                timeTxt = "%i:%02i" % (elapsed_min, elapsed_sec)
            if 'file' in song:
                filename = song['file']
                # get filename from path
                slash_pos = filename.rfind('/')
                if slash_pos >= 0:
                    filename = filename[slash_pos + 1:]
            else:
                filename = ">> END OF PLAYLIST <<"
            if 'name' in song:
                name = song['name']
            else:
                name = ""
            if 'title' in song:
                title = song['title']
            else:
                title = ""
            if name == "" and title == "":
                titleTxt = filename
            else:
                titleTxt = name
                #print "[%s] [%s]" % (name, title),
                if len (title) > 0:
                    if len (titleTxt) > 0:
                        titleTxt += ": "
                    titleTxt += title
            maxTitleLen = 21 * 4
            if len (titleTxt) < maxTitleLen:
#                titleTxt += " " * (maxTitleLen - len (titleTxt))
                pass
            else:
                titleTxt = titleTxt[:maxTitleLen]

            if menuState == 0:
                #########
                # COVER #
                #########
                if titleTxt != prevTitleTxt or forcePrintTitle:
                    # clear needed if font size changed!
                    self.menu.clearScreen()
                    self.menu.setFont(self.menu.FONT_SMALL)
                    self.menu.printStr(0, 25, titleTxt)
                    self.menu.setVolume(int(mpdvolume))
                    #self.menu.printStr(0, 8, titleTxt)
                    self.printDisk(disk)
                    self.printLink(link)
                    forcePrintTitle = False
                    # force printing the other ones, because screen was cleared
                    forcePrintStatus = True
                    forcePrintDisk = True
                    forcePrintTime = True
                if timeTxt != prevTimeTxt or forcePrintTime:
                    if len (timeTxt) <= 9:
                        self.menu.setFont(self.menu.FONT_BIG_NUMBERS)
                        timeTxt += " " * (9 - len (timeTxt))
                        self.menu.printStr(0, 0, timeTxt)
#               elif len (timeTxt) <= 10:
#                   self.menu.setFont(self.menu.FONT_MEDIUM_NUMBERS)
#                    timeTxt += " " * (10 - len (timeTxt))
#                   self.menu.printStr(0, 4, timeTxt)
                    elif len (timeTxt) <= 12:
                        self.menu.setFont(self.menu.FONT_NORMAL_NUMBERS)
                        timeTxt += " " * (12 - len (timeTxt))
                        self.menu.printStr(0, 4, timeTxt)
                    else:
                        self.menu.setFont(self.menu.FONT_SMALL)
                        self.menu.printStr(0, 4, timeTxt)
                    forcePrintTime = False
                if state != status['state'] or forcePrintStatus:
                    self.menu.setFont(self.menu.FONT_SMALL)
                    if status['state'] == 'play':
                        self.menu.printStr(0, 54, "\x80")
                    elif status['state'] == 'pause':
                        self.menu.printStr(0, 54, "\x82")
                    else:
                        self.menu.printStr(0, 54, "\x81")
                    state = status['state']
                    forcePrintStatus = False
                if disk != prevDisk or forcePrintDisk:
                    self.printDisk(disk)
                    prevDisk = disk
                    forcePrintDisk = False
                if link != prevLink or forcePrintLink:
                    self.printLink(link)
                    prevLink = link
                    forcePrintLink = False
                (volume, volumeChanged) = self.menu.getVolume()
                if volumeChanged:
                    # volume changed with the knob
                    print "\r\nradio->mpd", volume
                    self.mpdclient.setvol (volume)
                else:
                    if mpdvolume != status['volume']:
                        # volume changed on mpd
                        mpdvolume = status['volume']
                        print "\r\nmpd->radio", mpdvolume
                        self.menu.setVolume(int(mpdvolume))
            else:
                #########
                # MENU  #
                #########
                activatedMenu = self.menu.getActivatedMenu()
                if activatedMenu is not None:
                    if activatedMenu == 0:
                        print "seek"
                    elif activatedMenu == 1:
                        print "power off"
                        os.system("poweroff")
                    elif activatedMenu == 2:
                        print "Show IP"
                        output = self.runCommand("iwconfig wlan0")
                        ssid = "?"
                        link_quality = "?"
                        signal_level = "?"
                        ip = "?"
                        # .*? -> non-greedy .*
                        m = re.search("ESSID:\"(.*?)\"", output)
                        if m:
                            ssid = m.group(1)
                        m = re.search(r"Link Quality=(\S+)", output)
                        if m:
                            link_quality = m.group(1)
                        m = re.search(r"Signal level=(\S+)\s+(\S+)", output)
                        if m:
                            signal_level = m.group(1) + " " + m.group(2)
                        output = self.runCommand("ip addr show dev wlan0")
                        #m = re.search(r"inet (\n+.\n+.\n+.\n+)", output)
                        m = re.search(r"inet (\S+)", output)
                        if m:
                            ip = m.group(1)
                        self.menu.clearScreen()
                        self.menu.printStr(0, 0, "SSID: %s" % ssid)
                        self.menu.printStr(0, 10, "Link quality: %s" % link_quality)
                        self.menu.printStr(0, 20, "Signal level: %s" % signal_level)
                        self.menu.printStr(0, 30, "IP: %s" % ip)
                        time.sleep (10)
                    elif activatedMenu == 3:
                        print "WiFi AP mode"
                        self.menu.clearScreen()
                        self.menu.printStr(0, 0, "SSID: Radio")
                        self.menu.printStr(0, 10, "Pwd: radiogaga")
                        self.menu.printStr(0, 20, "IP: 192.168.10.1")
                        os.system("/root/wifi_ap.sh")
                        time.sleep (10)
                    elif activatedMenu == 4:
                        print "back"
                        # do nothing
                    # go back to cover
                    menuState = 0
                    forcePrintTitle = True
                    forcePrintTime = True

            if self.enablePrint:
                if titleTxt != prevTitleTxt:
                    print ""
                else:
                    print "\r",
		print "%i%%" % volume,
                print timeTxt,
                print titleTxt,
                #print timeTxt.encode('utf-8'),
                #print titleTxt.encode('utf-8'),
            #print filename, name, title,
            prevTimeTxt = timeTxt
            prevTitleTxt = titleTxt

if __name__ == "__main__":
    # make output unbuffered
    sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)
    app = App ()
    app.run ()

# vim:et:sw=4:nocindent:
