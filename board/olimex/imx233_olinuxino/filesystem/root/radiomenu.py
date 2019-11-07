#!/usr/bin/env python2
# Menu for internet radio
#
# Code starts: 2019-10-23 13:30:57
# Last modify: 2019-11-07 18:45:30 ivanovp {Time-stamp}

import mpd
import time
import sys
import os
import sys
import getopt
#import re
#import array
import serial

LAST_UPDATE_STR = "Last update: 2019-11-07 18:45:30 ivanovp {Time-stamp}"

if sys.hexversion >= 0x3000000:
    print "Python interpreter 2.x is needed."
    sys.exit (3)

class MenuControl:
    SERIAL_TIMEOUT_SEC = 0.1
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

    KEY_STOP    = 4
    KEY_PLAY    = 8
    KEY_MENU    = 16
    KEY_NEXT    = 32
    KEY_PREV    = 64

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
            cmd = command.encode(self.CODESET)
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
        return answer

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
        mpdvolume = 0
        status = self.mpdclient.status()
        if 'volume' in status:
            self.menu.setVolume(int(status['volume']))
            mpdvolume = status['volume']
	(volume, volumeChanged) = self.menu.getVolume()
	font = -1
	prevFont = -1
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
            key = self.menu.getKey()
            if key != 0:
                print "\r\nkey:", key
                if key & self.menu.KEY_PREV:
                    print "prev"
                    self.mpdclient.previous()
                if key & self.menu.KEY_NEXT:
                    print "next"
                    self.mpdclient.next()
                if key & self.menu.KEY_PLAY:
                    if status['state'] == 'play':
                        print "pause"
                        self.mpdclient.pause()
                    else:
                        print "play"
                        self.mpdclient.play()
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
                titleTxt = name + ": " + title
            maxTitleLen = 21 * 4
            if len (titleTxt) < maxTitleLen:
#                titleTxt += " " * (maxTitleLen - len (titleTxt))
                pass
            else:
                titleTxt = titleTxt[:maxTitleLen]
            if titleTxt != prevTitleTxt:
		if self.enablePrint:
                    print ""
                # clear needed if font size changed!
                self.menu.clearScreen()
                self.menu.setFont(self.menu.FONT_SMALL)
                self.menu.printStr(0, 25, titleTxt)
                self.menu.setVolume(int(mpdvolume))
                #self.menu.printStr(0, 8, titleTxt)
            else:
		if self.enablePrint:
                    print "\r",
            if timeTxt != prevTimeTxt:
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
            if self.enablePrint:
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
