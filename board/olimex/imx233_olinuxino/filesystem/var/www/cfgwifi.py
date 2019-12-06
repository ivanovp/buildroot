#!/usr/bin/python

# Import modules for CGI handling 
import cgi, cgitb 
import os

# Create instance of FieldStorage 
form = cgi.FieldStorage() 

# Get data from fields
ssid = form.getvalue('ssid')
pwd  = form.getvalue('pwd')

print "Content-type:text/html\r\n\r\n"
print "<html>"
print "<head>"
print "<title>Reconfigure WiFi</title>"
print "</head>"
print "<body>"
print "<p>SSID: %s<br>Password: %s</p>" % (ssid, pwd)
os.system("wpa_passphrase %s %s >/etc/wpa_supplicant.conf" % (ssid, pwd))
#os.system("sudo '/sbin/ifdown wlan0 2>&1'")
#os.system("sudo '/sbin/ifup wlan0 2>&1'")
os.system("sudo '/sbin/ifdown wlan0 2>/dev/null >/dev/null'")
os.system("sudo '/sbin/ifup wlan0 2>/dev/null >/dev/null'")
print "</body>"
print "</html>"

