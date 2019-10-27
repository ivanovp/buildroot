#!/usr/bin/env python2
# Menu for internet radio
#
# Code starts: 2019-10-23 13:30:57
# Last modify: 2019-10-27 21:33:04 ivanovp {Time-stamp}

import mpd
import time
import sys
import os
import sys
import getopt
#import re
#import array
import serial

LAST_UPDATE_STR = "Last update: 2019-10-27 21:33:04 ivanovp {Time-stamp}"

if sys.hexversion >= 0x3000000:
    print "Python interpreter 2.x is needed."
    sys.exit (3)

class MenuControl:
    SERIAL_TIMEOUT_SEC = 0.5
    SERIAL_PORT = "/dev/ttyAPP0"
    SERIAL_BAUD_RATE = 115200
    # Commands for LCD
    CMD_ECHO_DISABLE                    = "E0"
    CMD_ECHO_ENABLE                     = "E1"

    # Answer to command
    ANSWER_OK                           = 0x55
    ANSWER_ERROR                        = 0x5A
    NO_ANSWER                           = 0xAA

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
            cmd = command.encode()
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

    def printStr(self, x, y, string):
        cmd = "P%03i,%03i,%s" % (x, y, string)
        return self.sendCommand(cmd)
    
class App:
    VERSION_STR = "1.0.0"
    AUTHOR_STR = "Peter Ivanov <ivanovp@gmail.com>"
    DEFAULT_SERIAL_PORT = "/dev/ttyAPP0"

    def __init__ (self):
        self.verboseLevel = 5
        self.serialPort = self.DEFAULT_SERIAL_PORT

#        if len (sys.argv) < 2:
#            self.usage ()
#            sys.exit ()
    
        cntr = 1
        # Processing remaining switches
        try:
            opts, args = getopt.getopt(sys.argv[cntr:], "p:hv:", ["port=", "help", "verbose="])
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
        self.mpdclient = mpd.MPDClient(use_unicode=True)
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
        titleTxt = ""
        prevTitleTxt = ""
        while True:
            #self.mpdclient.idle()
            time.sleep(0.1)
            song = self.mpdclient.currentsong()
            status = self.mpdclient.status()
            elapsed_min = float (status['elapsed']) / 60
            elapsed_sec = float (status['elapsed']) % 60
            filename = song['file']
            print "\r",
            if 'duration' in status:
                duration_min = float (status['duration']) / 60
                duration_sec = float (status['duration']) % 60
                timeTxt = "%i:%02i/%i:%02i" % (elapsed_min, elapsed_sec, duration_min, duration_sec)
            else:
                timeTxt = "%i:%02i" % (elapsed_min, elapsed_sec)
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
            if titleTxt != prevTitleTxt:
                print ""
                self.menu.clearScreen()
                self.menu.printStr(0, 8, titleTxt)
            print timeTxt,
            print titleTxt,
            self.menu.printStr(0, 0, timeTxt)
            prevTitleTxt = titleTxt
            #print filename, name, title,

if __name__ == "__main__":
    # make output unbuffered
    sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)
    app = App ()
    app.run ()

# vim:et:sw=4:nocindent:
