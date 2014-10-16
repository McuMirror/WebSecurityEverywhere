#! /usr/bin/env python
# -*- coding: utf-8 -*-

##########################
#	 Autonomous internet security box
#
#    Copyright (C) 2014  Arcadia Labs / Stephane Guerreau
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##########################


##########################
# 5_11
# added random access point security key generation, with its menu page (only "generate a new key" feature for the moment)
# hostapd config file read / parse / save functions
# added upis True/False config variable to disable upis related features
######
# 5_9
# added ext ip check function with TOR check page (GET_IP_METHOD = 1 : apify, 2 : TOR check)
# added upis over temperature alert icon
# added display refresh delay setting
# TOR white/black list are now saved on exit, loaded on start
######
# 5_8
# added country based TOR relays white/black list functions
######
# 5_6
# moved TOR scripts to main data directory
# added configfiles directory with dnsmasq.conf, torrc
# removed old data subdirectory
######
# 5_5
# improved UPiS management
# added licence (GPL v3) and CLI notice
# enabled screen timeout
# improved rpi/bpi common code
# cleaned up main data directory
# moved GeoIP database to main data directory
######
# 5_4
# solved some UPiS management bugs (old code is still there for eventual future use)
# solved screen timeout bug
# changed the public ip check function to be more reliable (apify)
######
# 5_2
# changed menus
# added screen timeout function (disabled for now)
# added debug function
# improved rpi/bpi common code
# added basic UPiS / power management functions
######
# 5_1
# added rpi/bpi temperature common function
##########################

notice = "############\nAutonomous internet security box\nCopyright (C) 2014  Arcadia Labs / Stephane Guerreau\n\nThis program comes with ABSOLUTELY NO WARRANTY;\nThis is free software, and you are welcome to redistribute it under certain conditions;\nPlease see <http://opensource.org/licenses/GPL-3.0> for details.\n\nEmail contact : info@arcadia-labs.com\n############"

print(notice)

import io
import os
import pygame
from pygame.locals import *

import time
from time import sleep

import data 
from data import *

# Public IP - Deprecated
#import urllib2
#import socket
# import time
#import signal

# Public IP - apify
from requests import get
import urllib2
import socket

# ESSID
import array
import fcntl
# import socket
import struct

# Serial (UPiS) - Disabled
# - serial comm
#import serial
#ser = serial.Serial()
#ser.baudrate = 38400
#ser.port = "/dev/ttyAMA0"
#ser.timeout = 1
#ser.writeTimeout = 1

# I2C comm (UPiS)
# Unused for the moment, I need to find a way to convert BCD values to float
# import smbus
# bus = smbus.SMBus(1)

# Load / Save settings
import cPickle as pickle

# GPIO / PWM Backlight (old method)
#import subprocess
#import RPi.GPIO as GPIO

import numpy as np

# Initialization -----------------------------------------------------------

# I keep this one for a eventual future driver change
# from evdev import InputDevice, list_devices
# devices = map(InputDevice, list_devices())
# eventX=""
# for dev in devices:
	# if dev.name == "ADS7846 Touchscreen":
		# eventX = dev.fn
# print eventX

# be sure backlight is on
subprocess.call(['sudo sh -c "echo 0 > /sys/class/backlight/fb_ili9320/bl_power" &'], shell=True)

# ###FBTFT OLD METHOD
# Init framebuffer/touchscreen environment variables
# os.environ["SDL_FBDEV"] = "/dev/fb2"
# os.environ["SDL_VIDEO_CENTERED"] = "1"
# os.environ["SDL_MOUSEDRV"] = "TSLIB"
# os.environ["SDL_MOUSEDEV"] = "/dev/input/event2"

# os.environ["SDL_VIDEO_CENTERED"] = "1"
# #Init pygame and screen
# print "Initting..."
# pygame.init()
# print "Setting Mouse invisible..."
# pygame.mouse.set_visible(False)
# print "Setting fullscreen..."
# modes = pygame.display.list_modes(16)
# screen = pygame.display.set_mode((320, 240), FULLSCREEN, 16)
# #FBTFT OLD METHOD END

# ### FBTFT NEW METHOD
# Init framebuffer/touchscreen environment variables
# os.environ["SDL_VIDEODRIVER"] = "directfb"

if board_type == "rpi":		# RPi
	device = 'fb1'
elif board_type == "bpi":		# BPi
	device = 'fb2'
		

os.environ["SDL_FBDEV"] = "/dev/"+device+""
try:
	pygame.display.init()
except pygame.error:
	print 'device: {0} failed.'.format(device)
	
size = (pygame.display.Info().current_w, pygame.display.Info().current_h)
print "Framebuffer size: %d x %d" % (size[0], size[1])

# non-SPI touchscreen support
#os.environ["SDL_MOUSEDRV"] = "TSLIB"
#os.environ["SDL_MOUSEDEV"] = "/dev/input/touchscreen"

# Init pygame
print "Init Pygame..."
pygame.init()

disp_no = os.getenv("DISPLAY")
if disp_no:
	print "I'm running under X display = {0}".format(disp_no)
	print "- Starting windowed..."
	modes = pygame.display.list_modes(32)
	print ("- Available modes : "+str(modes))
	screen = pygame.display.set_mode((320, 240), RESIZABLE, 32)
else:	
	print "I'm running under the console"
	print "- Setting Mouse invisible..."
	if board_type == "rpi":
		pygame.mouse.set_visible(False)
	print "- Starting fullscreen..."
	modes = pygame.display.list_modes(16)
	print ("- Available modes : "+str(modes))
	screen = pygame.display.set_mode((320, 240), FULLSCREEN, 16)
# FBTFT NEW METHOD END

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
maxLength = {
	"interface": 16,
	"essid": 32
}
calls = {
	"SIOCGIWESSID": 0x8B1B
}

# Directories setup
data_py = os.path.abspath(os.path.dirname(__file__))
data_dir = os.path.normpath(os.path.join(data_py, '..', 'data'))

displayDelay = 0

# Get user & group IDs for file & folder creation
# (Want these to be 'pi' or other user, not root)
print "Get user & group IDs..."
s = os.getenv("SUDO_UID")
uid = int(s) if s else os.getuid()
s = os.getenv("SUDO_GID")
gid = int(s) if s else os.getgid()
		
def filepath(filename):
    return os.path.join(data_dir, filename)

def load(filename, mode='rb'):
    return open(os.path.join(data_dir, filename), mode)

def load_image(filename):
	filename = filepath(filename)
	try:
		image = pygame.image.load(filename)
		image = pygame.transform.scale(image, (image.get_width()*2, image.get_height()*2))
	except pygame.error:
		raise SystemExit, "Unable to load: " + filename
	return image.convert_alpha()
	
# GeoIP
## Quick Documentation ##
# Create your GeoIP instance with appropriate access flag. STANDARD reads data 
# from disk when needed, MEMORY_CACHE loads database into memory on instantiation 
# and MMAP_CACHE loads database into memory using mmap.
import GeoIP
gi = GeoIP.open(data.filepath('GeoLiteCity.dat'),GeoIP.GEOIP_STANDARD)

countryBlocked = []
countryForced = []			
			
ext_ip = ""
ext_ip_loc = ""
ext_ip_city_loc = ""
ip_check = 1
socket.setdefaulttimeout(GET_EXTIP_TIMEOUT)

eth0 = ""
wlan0 = ""
wlan1 = ""
usb0 = ""
tun0 = ""

ESSID = ""
wlan_quality = ""

cputemp = ""
load_average = ""

displayTimeout = time.time()
#displayDelay = 2
displayBacklight = True
backlightControl = False

extip_hide = False

page = 0

### UPiS PiCo interface ###
# Unused for the moment, I need to find a way to convert BCD values to int/float
#upis_adresses = [ 0x69,		# RTC Registers Direct Access Specification
#			0x6A, 			# UPiS Status
#			0x6B			# UPiS Control Commands
#			]
#upis_status = [ 0,			# Powering Mode
#				1,			# Mean value of Battery Voltage in 10 of mV in BCD format
#				2,			# Mean value of Voltage supplying RPi on P1 5V Pin in 10th of mV in BCD format
#				3,			# Mean value of Voltage supplying USB on P1 5V Pin in 10th of mV in BCD format
#				5,			# Mean value of Voltage supplying USB on P1 5V Pin in 10th of mV in BCD format
#				7,			# Mean value of Voltage supplying EPR on P1 5V Pin in 10th of mV in BCD format
#				9			# Mean value of current supplying UPiS+RPi in 10th of mA in BCD format
#			]

# Workaround with a C script (http://www.forum.pimodules.com/viewtopic.php?f=7&t=47#)
upis_status = [ 'p',			# Powering Mode
				'c',			# Return the UPiS temperature in centigrade
				'a',			# Return the UPiS+RPi current consumption in mA
				'b',			# Return the UPiS battery voltage in V
				'r',			# Return the RPi input voltage in V
				'u',			# Return the UPiS USB power input voltage in V
				'e'				# Return the UPiS external power input voltage in V
			]
			
pwr_mode = 0
bat_level = 0
rpi_level = 0
usb_level = 0
epr_level = 0
cm_level = 0
tmp = 0
pwr = 0
batt_cons = 0
curr_cons = 0
batt_perc = 0
serial_reading = False 

WifiAPkeyLenghtData = {}
WifiAPkeyLenghtData['WifiAPkeyLenghts'] = {'40':5,
'64':8,
'104':13,
'128':16,
'152':16,
'232':29,
'256':32}

# load pictures
# MENU PICTURES
img_left = pygame.image.load(data.filepath("icons/left_s.png"))			# 48x48
img_right = pygame.image.load(data.filepath("icons/right_s.png"))		# 48x48
img_prev = pygame.image.load(data.filepath("icons/prev.png"))			# 80x52
img_next = pygame.image.load(data.filepath("icons/next.png"))			# 80x52
img_ok = pygame.image.load(data.filepath("icons/ok.png"))				# 140x60
img_cancel = pygame.image.load(data.filepath("icons/cancel.png"))		# 140x60
img_newkey = pygame.image.load(data.filepath("icons/newkey.png"))		# 140x60

# this ugly variable will store arrows positions in pratical form for later use
m1_xy =  [[0, LCD_HEIGHT/2-img_left.get_height()/2], 
			[LCD_WIDTH-img_right.get_width(), LCD_HEIGHT/2-img_right.get_height()/2]]
# here is an example
m1_left_pos = pygame.Rect(m1_xy[0][0], m1_xy[0][1], img_left.get_width(), img_left.get_height())
m1_right_pos = pygame.Rect(m1_xy[1][0], m1_xy[1][1], img_right.get_width(), img_right.get_height())

m2_xy =  [[0, LCD_HEIGHT/4-img_left.get_height()/2], 
			[LCD_WIDTH-img_right.get_width(), LCD_HEIGHT/4-img_right.get_height()/2],
			[0, LCD_HEIGHT/2-img_left.get_height()/2],
			[LCD_WIDTH-img_right.get_width(), LCD_HEIGHT/2-img_right.get_height()/2]]
m2_left1_pos = pygame.Rect(m2_xy[0][0], m2_xy[0][1], img_left.get_width(), img_left.get_height())
m2_right1_pos = pygame.Rect(m2_xy[1][0], m2_xy[1][1], img_right.get_width(), img_right.get_height())
m2_left1b_pos = pygame.Rect(m2_xy[0][0]+48, m2_xy[0][1], img_left.get_width(), img_left.get_height())
m2_right1b_pos = pygame.Rect(m2_xy[1][0]-48, m2_xy[1][1], img_right.get_width(), img_right.get_height())

m2_left2_pos = pygame.Rect(m2_xy[2][0], m2_xy[2][1], img_left.get_width(), img_left.get_height())
m2_right2_pos = pygame.Rect(m2_xy[3][0], m2_xy[3][1], img_right.get_width(), img_right.get_height())
m2_left2b_pos = pygame.Rect(m2_xy[2][0]+48, m2_xy[2][1], img_left.get_width(), img_left.get_height())
m2_right2b_pos = pygame.Rect(m2_xy[3][0]-48, m2_xy[3][1], img_right.get_width(), img_right.get_height())

prevnext_xy = [[0,0], [LCD_WIDTH-img_prev.get_width(), 0]]
prev_pos = pygame.Rect(prevnext_xy[0][0], prevnext_xy[0][1], img_prev.get_width(), img_prev.get_height())
next_pos = pygame.Rect(prevnext_xy[1][0], prevnext_xy[1][1], img_next.get_width(), img_next.get_height())

img_ok_pos = pygame.Rect(LCD_WIDTH/2-img_ok.get_width()/2, LCD_HEIGHT-img_ok.get_height(), img_ok.get_width(), img_ok.get_height())
img_cancel_pos = pygame.Rect(LCD_WIDTH-img_cancel.get_width(), LCD_HEIGHT-img_cancel.get_height(), img_cancel.get_width(), img_cancel.get_height())
img_newkey_pos = pygame.Rect(LCD_WIDTH/2-img_newkey.get_width()/2, LCD_HEIGHT-img_newkey.get_height()*2, img_newkey.get_width(), img_newkey.get_height())

img_ok2_pos = pygame.Rect(0, LCD_HEIGHT-img_ok.get_height(), img_ok.get_width(), img_ok.get_height())

# INTERFACE PICTURES
fond = pygame.image.load(data.filepath(BACK_PICTURE))
template = pygame.image.load(data.filepath(template_PICTURE))

internet_on_32_logo = pygame.image.load(data.filepath("icons/"+str(NETWORKMAIN_ICONSIZE)+"/"+NETWORK_INTON))
internet_off_32_logo = pygame.image.load(data.filepath("icons/"+str(NETWORKMAIN_ICONSIZE)+"/"+NETWORK_INTOFF))
internet_tor_32_logo = pygame.image.load(data.filepath("icons/"+str(NETWORKMAIN_ICONSIZE)+"/"+NETWORK_INTTOR))
internet_vpn_32_logo = pygame.image.load(data.filepath("icons/"+str(NETWORKMAIN_ICONSIZE)+"/"+NETWORK_INTVPN))
client_on_32_logo = pygame.image.load(data.filepath("icons/"+str(NETWORKMAIN_ICONSIZE)+"/"+NETWORK_CLION))
client_off_32_logo = pygame.image.load(data.filepath("icons/"+str(NETWORKMAIN_ICONSIZE)+"/"+NETWORK_CLIOFF))
ap_on_16_logo = pygame.image.load(data.filepath("icons/"+str(TOPBAR_ICONSIZE)+"/"+TOPBAR_APON))
ap_off_16_logo = pygame.image.load(data.filepath("icons/"+str(TOPBAR_ICONSIZE)+"/"+TOPBAR_APOFF))
client_on_16_logo = pygame.image.load(data.filepath("icons/"+str(TOPBAR_ICONSIZE)+"/"+TOPBAR_CLION))
client_off_16_logo = pygame.image.load(data.filepath("icons/"+str(TOPBAR_ICONSIZE)+"/"+TOPBAR_CLIOFF))
eth_on_16_logo = pygame.image.load(data.filepath("icons/"+str(TOPBAR_ICONSIZE)+"/"+TOPBAR_ETHON))
eth_off_16_logo = pygame.image.load(data.filepath("icons/"+str(TOPBAR_ICONSIZE)+"/"+TOPBAR_ETHOFF))
usb_16_logo = pygame.image.load(data.filepath("icons/"+str(TOPBAR_ICONSIZE)+"/"+TOPBAR_USB))
tor_16_logo = pygame.image.load(data.filepath("icons/"+str(TOPBAR_ICONSIZE)+"/"+TOPBAR_TOR))
overtemp_icon = pygame.image.load(data.filepath("icons/"+str(TOPBAR_ICONSIZE)+"/"+TOPBAR_OVERTEMP))

tor_off_button = pygame.image.load(data.filepath("icons/"+str(MISC_ICONSIZE)+"/"+BOTTOMBAR_TOR_OFF))
tor_on_button = pygame.image.load(data.filepath("icons/"+str(MISC_ICONSIZE)+"/"+BOTTOMBAR_TOR_ON))
tor_x = 0+MARGIN_X
tor_y = LCD_HEIGHT-MISC_ICONSIZE-MARGIN_Y

vpn_off_button = pygame.image.load(data.filepath("icons/"+str(MISC_ICONSIZE)+"/"+BOTTOMBAR_VPN_OFF))
vpn_on_button = pygame.image.load(data.filepath("icons/"+str(MISC_ICONSIZE)+"/"+BOTTOMBAR_VPN_ON))
vpn_x = LCD_WIDTH-MISC_ICONSIZE-MARGIN_X
vpn_y = LCD_HEIGHT-MISC_ICONSIZE-MARGIN_Y

menu_button = pygame.image.load(data.filepath("icons/"+str(MISC_ICONSIZE)+"/"+BOTTOMBAR_MENU))
menu_button_x = LCD_WIDTH/2-MISC_ICONSIZE
menu_button_y = LCD_HEIGHT-MISC_ICONSIZE-MARGIN_Y

class ParseINI(dict):
	def __init__(self, f):
		self.f = f
		self.__read()
 
	def __read(self):
		with open(self.f, 'r') as f:
			dict = self
			for line in f:
				if not line.startswith("#") and not line.startswith(';') and line.strip() != "":
					line = line.replace('=', ':')
					line = line.replace(';', '#')
					index = line.find('#')
					line = line[:index]
					line = line.strip()
					if not self:
						dict['global'] = {}
						dict = dict['global']
					parts = line.split(":", 1)
					dict[parts[0].strip()] = parts[1].strip()
 
	def items(self):
		try:
			return self
		except KeyError:
			return []
			
def saveSettings():
	print "- Saving settings"
	try:
		outfile = open('config.pkl', 'wb')
		# Use a dictionary (rather than pickling 'raw' values) so
		# the number & order of things can change without breaking.
		print("-- ok")
		d = { 
			'displayDelay' : displayDelay,
			'countryBlocked' : countryBlocked,
			'countryForced' : countryForced,
			'WifiAPkeyLenght' : WifiAPkeyLenght
			}
		pickle.dump(d, outfile)
		outfile.close()
	except:
		print("-- error")
		pass

def loadSettings():
	global displayDelay
	global countryBlocked
	global countryForced
	global WifiAPkeyLenght
	print "- Loading settings"
	try:
		infile = open('config.pkl', 'rb')
		d = pickle.load(infile)
		infile.close()
		print("-- ok")
		if 'displayDelay' in d: displayDelay = d['displayDelay']
		if 'countryBlocked' in d: countryBlocked = d['countryBlocked']
		if 'countryForced' in d: countryForced = d['countryForced']
		if 'WifiAPkeyLenght' in d: WifiAPkeyLenght = d['WifiAPkeyLenght']
	except:
		print("-- error")
		pass
		
def getIP(url):
	if GET_IP_METHOD == 1:
		ip_checker_url = url
		address_regexp = re.compile ('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}')
		response = urllib2.urlopen(ip_checker_url).read()
		result = address_regexp.search(response)

		if result:
			return result.group()
		else:
			return None
		
	elif GET_IP_METHOD == 2:
		result = get('http://api.ipify.org').text
		return result
		
def generateKey(lenght):
	count = WifiAPkeyLenghtData['WifiAPkeyLenghts'][lenght]
	f = os.popen("dd if=/dev/random bs=1 count="+str(count)+" 2>/dev/null|xxd -ps")
	for i in f.readlines():
		i = i.rstrip('\n')
		key = i
	return key
	
def APgetnewkey(file, key):
	data = "ctrl_interface=/var/run/hostapd\n"
	data += "driver=rtl871xdrv\n"
	data += "ieee80211n=1\n"
	data += "ctrl_interface_group=0\n"
	data += "beacon_int=100\n"
	data += "interface=wlan0\n"
	data += "ssid=UnJailPiWifi\n"
	data += "hw_mode=g\n"
	data += "channel=6\n"
	data += "auth_algs=1\n"
	data += "wmm_enabled=1\n"
	data += "eap_reauth_period=360000000\n"
	data += "macaddr_acl=0\n"
	data += "ignore_broadcast_ssid=0\n"
	data += "wpa=2\n"
	data += "wpa_passphrase="+key+"\n"
	data += "wpa_key_mgmt=WPA-PSK\n"
	data += "wpa_pairwise=TKIP\n"
	data += "rsn_pairwise=CCMP\n"

	f = open(file, 'wb')
	f.write(data+"\n")
	f.close()
	
def write_hostapdConfig(file):
	data = "ctrl_interface="+hostapdConfig['global']['ctrl_interface']+"\n"
	data += "driver="+hostapdConfig['global']['driver']+"\n"
	data += "ieee80211n="+hostapdConfig['global']['ieee80211n']+"\n"
	data += "ctrl_interface_group="+hostapdConfig['global']['ctrl_interface_group']+"\n"
	data += "beacon_int="+hostapdConfig['global']['beacon_int']+"\n"
	data += "interface="+hostapdConfig['global']['interface']+"\n"
	data += "ssid="+hostapdConfig['global']['ssid']+"\n"
	data += "hw_mode="+hostapdConfig['global']['hw_mode']+"\n"
	data += "channel="+hostapdConfig['global']['channel']+"\n"
	data += "auth_algs="+hostapdConfig['global']['auth_algs']+"\n"
	data += "wmm_enabled="+hostapdConfig['global']['wmm_enabled']+"\n"
	data += "eap_reauth_period="+hostapdConfig['global']['eap_reauth_period']+"\n"
	data += "macaddr_acl="+hostapdConfig['global']['macaddr_acl']+"\n"
	data += "ignore_broadcast_ssid="+hostapdConfig['global']['ignore_broadcast_ssid']+"\n"
	data += "wpa="+hostapdConfig['global']['wpa']+"\n"
	data += "wpa_passphrase="+hostapdConfig['global']['wpa_passphrase']+"\n"
	data += "wpa_key_mgmt="+hostapdConfig['global']['wpa_key_mgmt']+"\n"
	data += "wpa_pairwise="+hostapdConfig['global']['wpa_pairwise']+"\n"
	data += "rsn_pairwise="+hostapdConfig['global']['rsn_pairwise']+"\n"

	f = open(file, 'wb')
	f.write(data+"\n")
	f.close()
	
def get_ESSID(interface):
	global ESSID
	"""Return the ESSID for an interface, or None if we aren't connected."""
	if os.path.exists('/sys/class/net/'+interface):
		try:
			essid = array.array("c", "\0" * maxLength["essid"])
			essidPointer, essidLength = essid.buffer_info()
			request = array.array("c",
				interface.ljust(maxLength["interface"], "\0") +
				struct.pack("PHH", essidPointer, essidLength, 0)
			)
			fcntl.ioctl(sock.fileno(), calls["SIOCGIWESSID"], request)
			field = essid.tostring().rstrip("\0")
			ESSID = field
			debug_msg("ESSID - "+field+"")
			return field
		except:
			field = "Client not connected"
			ESSID = field
			debug_msg("ESSID - "+field+"")
			return field			
	else:
		field = "Client : No interface"
		ESSID = field
		debug_msg("ESSID - "+field+"")
		return field

### TODO better...
def get_ext_ip():
	# check_ext_ip.stop()
	if ip_check == 1:
		start_time = time.time()
		global ext_ip
		global ext_ip_loc
		global ext_ip_city_loc
		global ext_ip_lat
		global ext_ip_lon
		global page
		try:
#			url = 'http://www.monip.org/'
#			page = urllib2.urlopen(url, timeout=GET_EXTIP_TIMEOUT).read()
#			ext_ip = page.split("IP : ")[1].split("<br>")[0]

#			ext_ip = get('http://api.ipify.org').text

			# ext_ip = getIP("http://api.ipify.org")
			ext_ip = getIP("https://check.torproject.org/")
			
			elapsed_time = time.time() - start_time
			gir = gi.record_by_addr(ext_ip)
			
			if gir != None:
				ext_ip_loc = format(gir['country_name'])
				ext_ip_city_loc = format(gir['city'])
				if ext_ip_city_loc == "None":
					ext_ip_city_loc = "Unknown City"
				ext_ip_lat = format(gir['latitude'])
				ext_ip_lon = format(gir['longitude'])
			else:
				ext_ip_loc = "???"
				ext_ip_city_loc = "? 1 ?"
				ext_ip_lat = "???"
				ext_ip_lon = "???"
				
		except urllib2.URLError as e:
			ext_ip = "null"
			ext_ip_loc = "null"
			ext_ip_city_loc = "null"
			ext_ip_lat = "null"
			ext_ip_lon = "null"
			elapsed_time = time.time() - start_time
			print(e)
		except IOError as e:
			ext_ip = "null"
			ext_ip_loc = "null"
			ext_ip_city_loc = "null"
			ext_ip_lat = "null"
			ext_ip_lon = "null"
			elapsed_time = time.time() - start_time
			print(e)
		except socket.timeout as e:
			ext_ip = "null"
			ext_ip_loc = "null"
			ext_ip_city_loc = "null"
			ext_ip_lat = "null"
			ext_ip_lon = "null"
			elapsed_time = time.time() - start_time
			print(e)
		except:
			ext_ip = "null"
			ext_ip_loc = "null"
			ext_ip_city_loc = "null"
			ext_ip_lat = "null"
			ext_ip_lon = "null"
			elapsed_time = time.time() - start_time
		ext_ip = format(ext_ip)
		debug_msg("NETWORK - EXT IP ("+format(elapsed_time)+"): "+ext_ip+" | "+ext_ip_loc+" | "+ext_ip_city_loc+" | "+ext_ip_lat+" | "+ext_ip_lon+"")
		#return(ext_ip)
	else:
		ext_ip = "SWITCHING IP"
		ext_ip_loc = "Please wait..."
		ext_ip_city_loc = ""
		ext_ip_lat = ""
		ext_ip_lon = ""
		debug_msg("NETWORK - EXT IP : ABORTED")
	# check_ext_ip.start()

def get_cputemp():
	global cputemp
	cputemp = read_cpu_temp()

def get_cpu_usage():
	global cpu_usage
	cpu_usage = read_cpu_usage()

def get_load_average():
	global load_average
	load_average = read_load_average()
	
def data_get_ext_ip():
	return get_ext_ip()

def data_get_ip_eth0():
	global eth0
	eth0 = get_iface_ip("eth0")

def data_get_ip_AP():
	global AP
	AP = get_iface_ip(WLAN_AP)
	if WLAN_AP == 'wlan0':
		global wlan0
		wlan0 = AP
	elif WLAN_AP == 'wlan1':
		global wlan1
		wlan1 = AP

def data_get_ip_CLI():
	global CLI
	CLI = get_iface_ip(WLAN_CLIENT)
	if WLAN_CLIENT == 'wlan0':
		global wlan0
		wlan0 = CLI
	elif WLAN_CLIENT == 'wlan1':
		global wlan1
		wlan1 = CLI

def data_get_ip_usb0():
	global usb0
	usb0 = get_iface_ip("usb0")
	
def data_get_ip_tun0():
	global tun0
	tun0 = get_iface_ip("tun0")

def data_get_ESSID(interface):
	return get_ESSID(interface)

def reset_wlan_ap(screen):
	show_popup(screen, "Reset Access Point")
	os.system('sudo killall hostapd')
	os.system('sudo ifdown '+WLAN_AP+'')
	os.system('sudo rm -rf /var/run/hostapd/'+WLAN_AP+'')

	iptables_restore()

	os.system('sudo ifup '+WLAN_AP+'')
	os.system('sudo hostapd -B /etc/hostapd/hostapd.conf &')
	os.system('sudo service dnsmasq restart')
	network_infos(screen)
	
def reset_wlan_client(screen):
	show_popup(screen, "Reset Client adapter")
	os.system('sudo ifdown '+WLAN_CLIENT+'')
	os.system('sudo ifup '+WLAN_CLIENT+' &')
	network_infos(screen)
	
def reset_eth(screen):
	show_popup(screen, "Reset ethernet interface")
	os.system('sudo ifdown eth0')
	os.system('sudo ifup eth0')
	os.system('sudo /etc/init.d/dnsmasq restart &')
	network_infos(screen)
	
def toggle_backlight():
	global displayBacklight	
	if displayBacklight == True:
		debug_msg("screen off")
		subprocess.call(['sudo sh -c "echo 1 > /sys/class/backlight/fb_ili9320/bl_power" &'], shell=True)
		displayBacklight = False
	else:
		debug_msg("screen on")
		subprocess.call(['sudo sh -c "echo 0 > /sys/class/backlight/fb_ili9320/bl_power" &'], shell=True)
		displayBacklight = True
    	
def read_upis():
	global pwr_mode, bat_level, rpi_level, usb_level, epr_level, cm_level, tmp
	global pwr, batt_cons, curr_cons, batt_perc
	global serial_reading
	
### I2C - Not working, need some data conversion (BCD to int / float)
#	pwr_mode = bus.read_byte_data(upis_adresses[1], 0)
#	bat_level = bus.read_byte_data(upis_adresses[1], 1)
#	rpi_level = bus.read_byte_data(upis_adresses[1], 3)
#	usb_level = bus.read_byte_data(upis_adresses[1], 5)
#	epr_level = bus.read_byte_data(upis_adresses[1], 7)
#	cm_level = bus.read_byte_data(upis_adresses[1], 9)

## Serial - Buggy, some additional UPiS automatic status messages break the function
#	battery_power = ['BAT', 'LPR']
#	usb_power = ['USB']
#	
#	if serial_reading == False:
#		serial_reading = True
#		try:
#			ser.open()	
#			ser.write("@PM\r\n")
#			sleep(0.1)
#			pwr_mode  = ser.read(35).strip()
#			debug_msg("UPiS pwr_mode : "+pwr_mode)
#		
#			if any(s in pwr_mode for s in battery_power):
#				pwr_mode = "BAT"
#			if any(s in pwr_mode for s in usb_power):
#				pwr_mode = "USB"	
#				ser.write("@USB\r\n")
#				sleep(0.1)
#				usb_ser  = ser.read(35).strip()
#				usb_ser = usb_ser.strip('USB Voltage:')
#				usb_ser = usb_ser.strip('V')
#				usb_level = float(usb_ser.strip())
#				debug_msg("UPiS usb_level : "+str(usb_level))
#			else:
#				pass
#		
#			ser.write("@BAT\r\n")
#			sleep(0.1)
#			bat_ser  = ser.read(35).strip()
#			bat_ser = bat_ser.strip('BAT Voltage:')
#			bat_ser = bat_ser.strip('V')
#			bat_level = float(bat_ser.strip())
#			debug_msg("UPiS bat_level : "+str(bat_level))
#		
#			ser.write("@RPI\r\n")
#			sleep(0.1)
#			rpi_ser  = ser.read(35).strip()
#			rpi_ser = rpi_ser.strip('RPi Voltage:')
#			rpi_ser = rpi_ser.strip('V')
#			rpi_level = float(rpi_ser.strip())
#			debug_msg("UPiS rpi_level : "+str(rpi_level))
#		
#			ser.write("@CUR\r\n")
#			sleep(0.1)
#			cm_ser  = ser.read(35).strip()
#			cm_ser = cm_ser.strip('UPiS Current:')
#			cm_ser = cm_ser.strip('mA')
#			cm_level = float(cm_ser.strip())
#			debug_msg("UPiS cm_level : "+str(cm_level))
#		
#			ser.write("@ANTMPC\r\n")
#			sleep(0.1)
#			tmp_ser  = ser.read(35).strip()
#			tmp_ser = tmp_ser.strip('Analog Sensor Temperature:')
#			tmp_ser = tmp_ser.strip('C')	
#			tmp = float(tmp_ser.strip())
#			debug_msg("UPiS tmp : "+str(tmp))
#			ser.close()
#		
#		
#			pwr = cm_level/1000*rpi_level
#			batt_cons = pwr+0.2*pwr
#			curr_cons = batt_cons/bat_level*1000
#			batt_perc = abs(4.11-bat_level*100/4.11-3.21)
#		except:
#			debug_msg("UPiS serial read error")
#		serial_reading = False
#	else:
#		debug_msg("UPiS serial not ready")

# Workaround C script
	f = os.popen("sudo upis -p")
	for i in f.readlines():
		pwr_mode = i
	
	f = os.popen("sudo upis -b")
	for i in f.readlines():
		bat_level = i
		
	f = os.popen("sudo upis -r")
	for i in f.readlines():
		rpi_level = i
		
	f = os.popen("sudo upis -u")
	for i in f.readlines():
		usb_level = i
		
	f = os.popen("sudo upis -e")
	for i in f.readlines():
		epr_level = i
		
	f = os.popen("sudo upis -a")
	for i in f.readlines():
		cm_level = i
		
	f = os.popen("sudo upis -c")
	for i in f.readlines():
		tmp = i
	
def read_upis_tmp():
	global tmp
	f = os.popen("sudo upis -c")
	for i in f.readlines():
		tmp = i
	
def update(background, screen):
	global info
	global page
	
	page = 0

	load_avg_string = load_average
	clock = get_time()
	dirty_rects = []

	y = 0+MARGIN_Y
	x = 0+MARGIN_X
	
	if BACK_COLOR != None:
		screen.fill(BACK_COLOR)
	
#	screen.fill(black)	
#	screen.blit(fond, (0,0))
	screen.blit(template, (0,0))
	
	if pygame.font:
		if AP != 'Not connected' and AP != 'Not found' :
			screen.blit(ap_on_16_logo, (x,y))
			x = x+TOPBAR_ICONSIZE
		if CLI != 'Not connected' and CLI != 'Not found':
			screen.blit(client_on_16_logo, (x,y))
			x = x+TOPBAR_ICONSIZE
		if eth0 != 'Not connected' and eth0 != 'Not found':
			screen.blit(eth_on_16_logo, (x,y))
			x = x+TOPBAR_ICONSIZE
		if usb0 != 'Not connected' and usb0 != 'Not found':
			screen.blit(usb_16_logo, (x,y))
			x = x+TOPBAR_ICONSIZE
			
		if check_tor() == True:
			screen.blit(tor_16_logo, (x,y))
			x = x+TOPBAR_ICONSIZE
			b_tor = screen.blit(tor_on_button, (tor_x, tor_y))
			torEnabled = True
		else:
			b_tor = screen.blit(tor_off_button, (tor_x, tor_y))
			torEnabled = False
			
		if check_vpn("tun0") == 1:
			b_vpn = screen.blit(vpn_on_button, (vpn_x, vpn_y))
		else:
			b_vpn = screen.blit(vpn_off_button, (vpn_x, vpn_y))
		
		if upis == True:
			tmp_float = float(tmp)
			if tmp_float >= UPIS_TEMP_ALERT:
				x = LCD_WIDTH-overtemp_icon.get_width()-5
				screen.blit(overtemp_icon, (x,y))
			else:
				x = LCD_WIDTH-5
		else:
			x = LCD_WIDTH-5
			
		font = pygame.font.Font(filepath(TOPBAR_FONT), TOPBAR_FONTSIZE)
		label = font.render(''+cputemp+' C, '+load_average+'%', 1, (green))
		screen.blit(label, (x-label.get_width()-5,y))
		
		font = pygame.font.Font(filepath(CLOCK_FONT), CLOCK_FONTSIZE)
		label = font.render(clock, 1, (CLOCK_FONTCOLOR))
		screen.blit(label, (LCD_WIDTH/2-label.get_width()/2,y))
			
		x = 0 + MARGIN_X
		y = y + font.get_height()
		font = pygame.font.Font(filepath(MAIN_FONT), PAGETITLE_FONTSIZE)
		label = font.render("UnJailPi", 1, (PAGETITLE_FONTCOLOR))
		screen.blit(label, (LCD_WIDTH-label.get_width()-MARGIN_X,y))
		
		part1_y = y+font.get_height()+SPACE
		if ext_ip != 'null':
			if check_tor() == True:
				screen.blit(internet_tor_32_logo, (17,65))
			else:
				if check_vpn("tun0") == True:
					screen.blit(internet_vpn_32_logo, (17,65))
				else:
					screen.blit(internet_on_32_logo, (17,65))
				
				
			label_x = x+NETWORKMAIN_ICONSIZE+SPACE
			label_y = part1_y+SPACE

			font = pygame.font.Font(filepath(MAIN_FONT), MAIN_FONTSIZE)
			if torEnabled == True:
				if extip_hide == True:
					label = font.render("real ip hidden", 1, (white))
				else:
					label = font.render(ext_ip, 1, (white))
			else:
				if extip_hide == True:
					label = font.render("real ip hidden", 1, (white))
				else:
					label = font.render(ext_ip, 1, (white))
				
			screen.blit(label, (55,label_y))
			label_y = label_y+font.get_height()+SPACE	
			
			font = pygame.font.Font(filepath(MAIN_FONT), MAIN_FONTSIZE)
			label = font.render(ext_ip_loc, 1, (white))
			screen.blit(label, (55,label_y))
			label_y = label_y+font.get_height()+SPACE	

			font = pygame.font.Font(filepath(MAIN_FONT), MAIN_FONTSIZE)
			label = font.render(ext_ip_city_loc, 1, (white))
			screen.blit(label, (55,label_y))
		else:
			screen.blit(internet_off_32_logo, (17,65))
			label_x = x+NETWORKMAIN_ICONSIZE+SPACE
			label_y = part1_y+SPACE

			font = pygame.font.Font(filepath(MAIN_FONT), MAIN_FONTSIZE)
			label = font.render("NO INTERNET", 1, (white))
			screen.blit(label, (55,label_y))
			label_y = label_y+font.get_height()+SPACE	
			
			font = pygame.font.Font(filepath(MAIN_FONT), MAIN_FONTSIZE)
			label = font.render("", 1, (white))
			screen.blit(label, (55,label_y))
			label_y = label_y+font.get_height()+SPACE	

			font = pygame.font.Font(filepath(MAIN_FONT), MAIN_FONTSIZE)
			label = font.render("", 1, (white))
			screen.blit(label, (55,label_y))

		y = label_y+font.get_height()+6
	
		if wlan1 != 'null':
			screen.blit(client_on_32_logo, (LCD_WIDTH / 2,part1_y+8))
			label_x = LCD_WIDTH / 2 + NETWORKMAIN_ICONSIZE + SPACE
			label_y = part1_y+SPACE

			font = pygame.font.Font(filepath(MAIN_FONT), MAIN_FONTSIZE)
			label = font.render(ESSID, 1, (white))
			screen.blit(label, (label_x,label_y))
			label_y = label_y+font.get_height()+SPACE
		else:
			screen.blit(client_off_32_logo, (x,part1_y+8))
			label_x = NETWORKMAIN_ICONSIZE+SPACE
			label_y = y+SPACE

			font = pygame.font.Font(filepath(MAIN_FONT), MAIN_FONTSIZE)
			label = font.render(ESSID, 1, (black))
			screen.blit(label, (label_x,label_y))
			label_y = label_y+font.get_height()+SPACE		

		x = MARGIN_X
		
		if eth0 != 'null':
			
			label_x = 64
			label_y = 114
			font = pygame.font.Font(filepath(MAIN_FONT), MAIN_FONTSIZE)	
			label = font.render(eth0, 1, (white))
			screen.blit(label, (label_x,label_y))
			y = y+font.get_height()+SPACE
		
		if wlan0 != 'null':
			
			label_x = 64
			label_y = label_y + 22
			font = pygame.font.Font(filepath(MAIN_FONT), MAIN_FONTSIZE)			
			label = font.render(wlan0, 1, (white))
			screen.blit(label, (label_x,label_y))
			y = y+font.get_height()+SPACE
			
		if tun0 != 'null':
			
			label_x = 214
			label_y = 114
			font = pygame.font.Font(filepath(MAIN_FONT), MAIN_FONTSIZE)
			label = font.render(tun0, 1, (white))
			screen.blit(label, (label_x,label_y))
			
		if wlan1 != 'null':
			
			label_x = 214
			label_y = label_y + 22
			font = pygame.font.Font(filepath(MAIN_FONT), MAIN_FONTSIZE)			
			label = font.render(wlan1, 1, (white))
			screen.blit(label, (label_x,label_y))
			y = y+font.get_height()+SPACE

		if usb0 != 'null':
			
			label_x = 214
			label_y = label_y + 22
			font = pygame.font.Font(filepath(MAIN_FONT), MAIN_FONTSIZE)
			label = font.render(usb0, 1, (white))
			screen.blit(label, (label_x,label_y))
			y = y+font.get_height()+SPACE
			
		
		
		b_menu = screen.blit(menu_button, (menu_button_x, menu_button_y))
		
	return dirty_rects
	
def power_screen(background, screen):
	global page
	
	page = 1
	
	load_avg_string = load_average
	clock = get_time()
	dirty_rects = []

	y = 0+MARGIN_Y
	x = 0+MARGIN_X
	
	if BACK_COLOR != None:
		screen.fill(BACK_COLOR)

	screen.fill(black)
	font = pygame.font.Font(pygame.font.get_default_font(),18)

	if pygame.font:
#		pwr_mode_str = str(pwr_mode)
		if pwr_mode == "1":
			pwr_mode_label = font.render("External Power", 1, (red))
		elif pwr_mode == "2":
			pwr_mode_label = font.render("UPiS USB Power", 1, (red))
			usb_level_label = font.render("USB volt : "+str(float(usb_level))+"V", 1, (white))
		elif pwr_mode == "3":
			pwr_mode_label = font.render("Raspberry Pi USB Power", 1, (red))
		elif pwr_mode == "4":
			pwr_mode_label = font.render("Battery Power", 1, (red))
		elif pwr_mode == "5":
			pwr_mode_label = font.render("Low Power", 1, (red))
		
		else:
			pwr_mode_label = font.render("Unknown source : "+str(pwr_mode), 1, (red))
		
		bat_level_label = font.render("Batt volt : "+str(bat_level)+"V", 1, (white))
		rpi_level_label = font.render("RPi volt  : "+str(rpi_level)+"V", 1, (white))		
		cm_level_label = font.render("RPi amps : "+str(cm_level)+"mA", 1, (white))
		epr_level_label = font.render("Ext power volt : "+str(epr_level)+"V", 1, (white))
		tmp_label = font.render(str(tmp)+"C", 1, (white))
#			pwr_label = font.render(str(float(pwr))+"Watts", 1, (white))
#			batt_cons_label = font.render(str(float(batt_cons))+"Watts", 1, (white))
#			curr_cons_label = font.render(str(float(curr_cons))+"mA", 1, (white))
#			batt_perc_label = font.render(str(int(batt_perc))+"%", 1, (white))
	
		y = 0+SPACE
		screen.blit(pwr_mode_label, (0,y))
		y = y+font.get_height()+SPACE
		screen.blit(bat_level_label, (0,y))
		y = y+font.get_height()+SPACE
		screen.blit(rpi_level_label, (0,y))
		y = y+font.get_height()+SPACE
		if pwr_mode == '1':
			screen.blit(epr_level_label, (0,y))
			y = y+font.get_height()+SPACE
		elif pwr_mode == '2':
			screen.blit(usb_level_label, (0,y))
			y = y+font.get_height()+SPACE
		screen.blit(cm_level_label, (0,y))
		y = y+font.get_height()+SPACE
		screen.blit(tmp_label, (0,y))
#		y = y+font.get_height()+SPACE
#		screen.blit(pwr_label, (0,y))
#			y = y+font.get_height()+SPACE
#			screen.blit(batt_cons_label, (0,y))
#			y = y+font.get_height()+SPACE
#			screen.blit(curr_cons_label, (0,y))
#			y = y+font.get_height()+SPACE
#			screen.blit(batt_perc_label, (0,y))
	
		b_menu = screen.blit(menu_button, (menu_button_x, menu_button_y))
		
		return dirty_rects
	
def update_event(screen):
	global ip_check
	global ext_ip
	global ext_ip_loc
	global ext_ip_city_loc
	global displayBacklight
	global displayTimeout
	
	for e in pygame.event.get():
		if e.type == pygame.MOUSEBUTTONDOWN:
			displayTimeout = time.time()
			pos = pygame.mouse.get_pos()
			
			if displayBacklight == True:
				b_menu_p = pygame.Rect(menu_button_x, menu_button_y, BOTTOMBAR_ICONSIZE*2, BOTTOMBAR_ICONSIZE)
				
				if page == 0:
					b_tor_p = pygame.Rect(tor_x, tor_y, BOTTOMBAR_ICONSIZE, BOTTOMBAR_ICONSIZE)
					b_vpn_p = pygame.Rect(vpn_x, vpn_y, BOTTOMBAR_ICONSIZE, BOTTOMBAR_ICONSIZE)
				
					if b_tor_p.collidepoint(pos):
						ip_check = 0
				
						if check_tor() == True:
							ext_ip = "RESTORING IP"
							ext_ip_loc = "Please wait..."
							ext_ip_city_loc = ""
#							show_popup(screen, "Restoring normal IP")
#							os.system('sudo service tor stop &')			

							Tor_Stop(screen)
							iptables_restore()
	
						else:
							show_popup(screen, "Getting new internet IP")
							ext_ip = "CHANGING IP"
							ext_ip_loc = "Please wait..."
							ext_ip_city_loc = ""
							
							os.system('sudo service tor start')
							os.system('sudo iptables -F')
							os.system('sudo iptables -t nat -F')
							
							# iptables
							if eth0 != 'null':
								os.system('sudo sh '+data.filepath('scripts/tor/tor_eth0_start.sh')+' &')
							if usb0 != 'null':
								os.system('sudo sh '+data.filepath('scripts/tor/tor_usb0_start.sh')+' &')
							if wlan1 != 'null':
								os.system('sudo sh '+data.filepath('scripts/tor/tor_wlan1_start.sh')+' &')
					
						ip_check = 1
					if b_vpn_p.collidepoint(pos):
						if check_vpn("tun0") == 1:
							ext_ip = "RESTORING IP"
							ext_ip_loc = "Please wait..."
							ext_ip_city_loc = ""
							show_popup(screen, "Restoring normal IP")
							Openvpn_Stop()
							iptables_restore()
						else:
							if check_tor() == True:
								ext_ip = "RESTORING IP"
								ext_ip_loc = "Please wait..."
								ext_ip_city_loc = ""
								show_popup(screen, "Stopping TOR")
								os.system('sudo service tor stop &')	
							show_popup(screen, "Starting VPN client")		

							iptables_openvpn()
							Openvpn_Start()						
				
				if b_menu_p.collidepoint(pos):
					if page == 0:
						check_ext_ip.stop()
						check_cputemp.stop()
						check_upis_tmp.stop()
						check_ip_eth0.stop()
						check_ip_AP.stop()
						check_ip_CLI.stop()
						check_ip_usb0.stop()
						check_ip_tun0.stop()
						check_essid.stop()
						check_load_average.stop()
					
					if page == 1:
						check_power.stop()
				
#					screen.fill((0, 0, 0))
#					pygame.display.flip()
					options_menu(screen)
			else:
				toggle_backlight()
#				displayTimeout = time.time()
#				displayBacklight = True	
		
		
		if e.type == KEYDOWN:
			if e.key in (K_SPACE, K_RETURN):
				
				check_ext_ip.stop()
				check_cputemp.stop()
				check_upis_tmp.stop()
				check_ip_eth0.stop()
				check_ip_AP.stop()
				check_ip_CLI.stop()
				check_ip_usb0.stop()
				check_ip_tun0.stop()
				check_essid.stop()
				check_load_average.stop()
				
#				screen.fill((0, 0, 0))
#				pygame.display.flip()
				menu(screen)
			if e.key == pygame.K_DOWN:
				check_ext_ip.stop()
				ip_check = 0
				ext_ip = "SWITCHING IP"
				ext_ip_loc = "Please wait..."
				ext_ip_city_loc = ""
				if process_exists("openvpn") == True:
					os.system('sudo nohup killall openvpn > /dev/null 2>&1 &')
				if process_exists("tor") == True:
					show_popup(screen, "Getting new internet ID")
					os.system('sudo service tor start &')
#					os.system('sudo /home/pi/scripts/tor/tor_restart.sh &')
				else:
					show_popup(screen, "Changing internet ID")		
					os.system('sudo service tor stop &')
#					os.system('sudo /home/pi/scripts/tor/tor_start.sh &')
				get_ext_ip()
				ip_check = 1
				check_ext_ip.start()
				
def iptables_restore():
	os.system('sudo iptables -F')
	os.system('sudo iptables -t nat -F')
	os.system('echo 1 > /proc/sys/net/ipv4/ip_forward')
	os.system('sudo iptables -t nat -A POSTROUTING -o wlan1 -j MASQUERADE')
	os.system('sudo iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE')
	os.system('sudo iptables -t nat -A POSTROUTING -o usb0 -j MASQUERADE')
	os.system('sudo iptables -A FORWARD -i wlan1 -o wlan0 -m state --state RELATED,ESTABLISHED -j ACCEPT')
	os.system('sudo iptables -A FORWARD -i wlan0 -o wlan1 -j ACCEPT		')		
	os.system('sudo iptables -A FORWARD -i eth0 -o wlan0 -m state --state RELATED,ESTABLISHED -j ACCEPT')
	os.system('sudo iptables -A FORWARD -i wlan0 -o eth0 -j ACCEPT')
	os.system('sudo iptables -A FORWARD -i usb0 -o wlan0 -m state --state RELATED,ESTABLISHED -j ACCEPT')
	os.system('sudo iptables -A FORWARD -i wlan0 -o usb0 -j ACCEPT		')		

	os.system('sudo iptables -t nat -I PREROUTING -p tcp --dport 53 -j REDIRECT --to-ports 53')
	os.system('sudo iptables -t nat -I PREROUTING -p udp --dport 53 -j REDIRECT --to-ports 53')
	
def iptables_openvpn():
	os.system('sudo iptables -F')
	os.system('sudo iptables -t nat -F')
	os.system('echo 1 > /proc/sys/net/ipv4/ip_forward')
	os.system('sudo iptables -t nat -A POSTROUTING -o tun0 -j MASQUERADE')
#	os.system('sudo iptables -A FORWARD -i tun0 -o '+WLAN_CLIENT+' -m state --state RELATED,ESTABLISHED -j ACCEPT')
#	os.system('sudo iptables -A FORWARD -i '+WLAN_CLIENT+' -o tun0 -j ACCEPT')

	os.system('sudo iptables -A FORWARD -i tun0 -o wlan1 -m state --state RELATED,ESTABLISHED -j ACCEPT')
	os.system('sudo iptables -A FORWARD -i wlan1 -o tun0 -j ACCEPT')
	os.system('sudo iptables -A FORWARD -i tun0 -o eth0 -m state --state RELATED,ESTABLISHED -j ACCEPT')
	os.system('sudo iptables -A FORWARD -i eth0 -o tun0 -j ACCEPT')
	os.system('sudo iptables -A FORWARD -i tun0 -o usb0 -m state --state RELATED,ESTABLISHED -j ACCEPT')
	os.system('sudo iptables -A FORWARD -i usb0 -o tun0 -j ACCEPT')

def adblock_update():
	os.system('sudo /home/pi/scripts/dnsmasq/dnsmasq_ad_list.sh')
					
def check_tor():
#	os.system("tor --quiet &")
	ps_info = subprocess.check_output(["ps", "-A"])
	ps_info = str(ps_info)
	if re.search(r'\stor\s', ps_info): return True
	else: return False
	
def check_vpn(interface):
	if os.path.exists('/sys/class/net/'+interface):
		try:
			s = subprocess.check_output(["ip","addr","show",interface])
			ip = s.split('\n')[2].strip().split(' ')[1].split('/')[0]
			return 1
		except:
			return 2
	else:
		return 0

def bootmenu():
	os.system('sudo python /home/pi/scripts/pygame/bootmenu_2/start.py &')
	raise SystemExit
		
def network_infos(screen):
	global displayTimeout
	global displayBacklight
	
	font = pygame.font.Font(filepath(MAIN_FONT), MAIN_FONTSIZE)
	black = pygame.Surface((LCD_WIDTH, LCD_HEIGHT))
	
	background = pygame.Surface((LCD_WIDTH, LCD_HEIGHT)).convert()
	surf = pygame.Surface((LCD_WIDTH, LCD_HEIGHT)).convert()
	popup = pygame.Surface((LCD_WIDTH, LCD_HEIGHT)).convert()
	
	# if BACK_COLOR != None:
		# screen.fill(BACK_COLOR)
	global check_cputemp
	global check_ip_eth0
	global check_ip_AP
	global check_ip_CLI
	global check_ip_usb0
	global check_ip_tun0
	global check_essid
	global check_ext_ip
	global check_upis_tmp
	# global check_cputemp
	# global check_uptime
	# global check_cpu_usage
	global check_load_average
	
	check_cputemp = MyTimer(GET_CPUTEMP_DELAY, get_cputemp)
	check_upis_tmp = MyTimer(GET_UPIS_TMP_DELAY, read_upis_tmp)
	check_ip_eth0 = MyTimer(GET_IP_DELAY, data_get_ip_eth0)
	check_ip_AP = MyTimer(GET_IP_DELAY, data_get_ip_AP)
	check_ip_CLI = MyTimer(GET_IP_DELAY, data_get_ip_CLI)
	check_ip_usb0 = MyTimer(GET_IP_DELAY, data_get_ip_usb0)
	check_ip_tun0 = MyTimer(GET_IP_DELAY, data_get_ip_tun0)
	check_essid = MyTimer(GET_ESSID_DELAY, get_ESSID, [WLAN_CLIENT])
	check_ext_ip = MyTimer(GET_EXTIP_DELAY, get_ext_ip)
	check_load_average = MyTimer(GET_LOAD_AVERAGE_DELAY, get_load_average)
	
	get_ext_ip()
	get_cputemp()
	get_load_average()
	read_upis_tmp()
	get_ESSID(WLAN_CLIENT)
	data_get_ip_eth0()
	data_get_ip_AP()
	data_get_ip_CLI()
	data_get_ip_usb0()
	data_get_ip_tun0()
	#get_ext_ip()
	
	check_cputemp.start()
	check_upis_tmp.start()
	check_ip_eth0.start()
	check_ip_AP.start()
	check_ip_CLI.start()
	check_ip_usb0.start()
	check_ip_tun0.start()
	check_essid.start()
	check_ext_ip.start()
	# check_cputemp.start()
	# check_uptime.start()
	# check_cpu_usage.start()
	check_load_average.start()
	
	# reset backlight count
	displayTimeout = time.time()
	
	while 1:
		y = 0	
		now = time.time()
		if displayBacklight == True:
			if now - displayTimeout >= displayDelayData[displayDelay]:
				if displayDelay != 0:
					toggle_backlight()
		
		update(background, surf)
		update_event(screen)
	
		# screen.fill((0, 0, 0))
		rotatedscreen = pygame.transform.rotate(surf, 0)
		screen.blit(rotatedscreen, (0, 0))
	
		pygame.display.flip()
		pygame.time.wait(REFRESH_RATE)
		
def power_infos(screen):
	global displayTimeout
	global displayBacklight
	
	global check_power
	
	check_power = MyTimer(5, read_upis)
	read_upis()
	check_power.start()
	
	font = pygame.font.Font(filepath(MAIN_FONT), MAIN_FONTSIZE)
	black = pygame.Surface((LCD_WIDTH, LCD_HEIGHT))
	
	background = pygame.Surface((LCD_WIDTH, LCD_HEIGHT)).convert()
	surf = pygame.Surface((LCD_WIDTH, LCD_HEIGHT)).convert()
	popup = pygame.Surface((LCD_WIDTH, LCD_HEIGHT)).convert()
	
	# if BACK_COLOR != None:
		# screen.fill(BACK_COLOR)
	
	# reset backlight count
	displayTimeout = time.time()
	
	while 1:
		y = 0
		now = time.time()
		if displayBacklight == True:
			if now - displayTimeout >= displayDelayData[displayDelay]:
				if displayDelay != 0:
					toggle_backlight()
		
		power_screen(background, surf)
		update_event(screen)
	
		# screen.fill((0, 0, 0))
		rotatedscreen = pygame.transform.rotate(surf, 0)
		screen.blit(rotatedscreen, (0, 0))
	
		pygame.display.flip()
		pygame.time.wait(REFRESH_RATE)

#################
# ---- MENUS ----
#################

menupos = 0

def options_menu(screen):
	screen.fill(black)
	# check_tor()
	
	while True:
		choice = menu0(screen, mainmenuData, "Options")	
		if choice == 0 : network_menu(screen)
		if choice == 1 : settings_menu(screen)
		if choice == 2 : misc_menu(screen)
		if choice == 3 : system_menu(screen)
		if choice == len(mainmenuData)-1 : network_infos(screen)
		pygame.display.flip()

def network_menu(screen):
	screen.fill(black)
	# check_tor()
	
	while True:
		choice = menu0(screen, networkmenuData, "Network")		
		if choice == 0 : reset_wlan_ap(screen)
		if choice == 1 : reset_wlan_client(screen)
		if choice == 2 : reset_eth(screen)
		if choice == 3 : tor_country_settings(screen)
		if choice == 4 : changeKey_menu(screen)
		if choice == len(networkmenuData)-1 : options_menu(screen)
		pygame.display.flip()

def settings_menu(screen):
	screen.fill(black)
	while True:
		choice = menu0(screen, settingsmenuData, "Options")	
		if choice == 0 : changeValue_menu(screen, displayDelayData, displayDelay, "Display Timeout", " seconds")
		if choice == len(settingsmenuData)-1 : options_menu(screen)
		pygame.display.flip()
		
def misc_menu(screen):
	screen.fill(black)
	while True:
		choice = menu0(screen, miscmenuData, "Options")	
		if choice == 0 : power_infos(screen)
		if choice == len(miscmenuData)-1 : options_menu(screen)
		pygame.display.flip()
		
def system_menu(screen):
	screen.fill(black)
	# check_tor()
	
	while True:
		choice = menu0(screen, systemmenuData, "System")
		if choice == 0 : bootmenu()
		if choice == 1 : 
			saveSettings()
			exit()
		if choice == 2 : 
			saveSettings()
			Reboot(screen)
		if choice == 3 : 
			saveSettings()
			Shutdown(screen)
		if choice == len(systemmenuData)-1 : options_menu(screen)
		pygame.display.flip()

def menu0(screen, options, title, titlesize=22, choicesize = 18, titlecolor=(255,255,255), choicecolor=(255,0,0)):	
	global menupos
	menupos = 0
	x = len(options)-1
	
	while True:
		screen.fill(black)
		
		font = pygame.font.Font(pygame.font.get_default_font(),titlesize)
		label = font.render(title, 1, (titlecolor))
		
		
		screen.blit(label, (LCD_WIDTH/2-label.get_width()/2,0+10))
	
		screen.blit(img_left, (m1_xy[0][0], m1_xy[0][1]))
		screen.blit(img_right, (m1_xy[1][0], m1_xy[1][1]))
	
		screen.blit(img_ok, (LCD_WIDTH/2-img_ok.get_width()/2, LCD_HEIGHT-img_ok.get_height()))
#		screen.blit(img_cancel, (LCD_WIDTH-img_cancel.get_width(), LCD_HEIGHT-img_cancel.get_height()))
	
		# Touchscreen
		for e in pygame.event.get():
			if e.type == pygame.MOUSEBUTTONDOWN:
				pos = pygame.mouse.get_pos()
							
				if m1_left_pos.collidepoint(pos):	
					if menupos == 0:
						menupos = x
					else:
						menupos = menupos-1
#					debug_msg(menupos)
						
				if m1_right_pos.collidepoint(pos):
					if menupos == x:
						menupos = 0
					else:					
						menupos = menupos+1
#					debug_msg(menupos)
						
				if img_ok_pos.collidepoint(pos):
#					debug_msg("ok")
#					debug_msg(menupos)
					return menupos
					break
					
					
#				if img_cancel_pos.collidepoint(pos):
#					print"cancel"
		
		text = str(options[menupos])
		font = pygame.font.Font(pygame.font.get_default_font(),choicesize)
		label = font.render(text, 1, (choicecolor))
					 
		screen.blit(label, (LCD_WIDTH/2-label.get_width()/2,LCD_HEIGHT/2-font.get_height()/2))
				
		pygame.display.flip()	
		
def changeValue_menu(screen, option, n, title, unit, titlesize=22, choicesize = 18, titlecolor=(255,255,255), choicecolor=(255,0,0)):	
	global displayDelay
	i = n
	x = len(option)-1
	
	while True:
		screen.fill(black)		

		font = pygame.font.Font(pygame.font.get_default_font(),titlesize)
		label = font.render(title, 1, (white))
			
		screen.blit(label, (LCD_WIDTH/2-label.get_width()/2,0+10))
	
		screen.blit(img_left, (m1_xy[0][0], m1_xy[0][1]))
		screen.blit(img_right, (m1_xy[1][0], m1_xy[1][1]))
	
		screen.blit(img_ok, (0, LCD_HEIGHT-img_ok.get_height()))
		screen.blit(img_cancel, (LCD_WIDTH-img_cancel.get_width(), LCD_HEIGHT-img_cancel.get_height()))
	
		# Touchscreen
		for e in pygame.event.get():
			if e.type == pygame.MOUSEBUTTONDOWN:
				pos = pygame.mouse.get_pos()
							
				if m1_left_pos.collidepoint(pos):	
					if i == 0:
						i = x
					else:
						i = i-1
						
				if m1_right_pos.collidepoint(pos):
					if i == x:
						i = 0
					else:					
						i = i+1
						
				if img_ok2_pos.collidepoint(pos):
						
					if option == displayDelayData:
						displayDelay = i
					saveSettings()
					network_infos(screen)
					
				if img_cancel_pos.collidepoint(pos):

					network_infos(screen)
		
		font = pygame.font.Font(pygame.font.get_default_font(),choicesize)
		text = str(option[i])
		text+=unit
		if i == n:
			label = font.render(text, 1, (green))
		else:
			label = font.render(text, 1, (choicecolor))
					 
		screen.blit(label, (LCD_WIDTH/2-label.get_width()/2,LCD_HEIGHT/2-font.get_height()/2))
				
		pygame.display.flip()
		
		
def changeKey_menu(screen, titlesize=22, choicesize = 16, titlecolor=(255,255,255), choicecolor=(255,255,255)):	
	global hostapdConfig
	hostapdConfig = ParseINI('/etc/hostapd/hostapd.conf')
	key = hostapdConfig['global']['wpa_passphrase']
	old_key = key
	# newkey = key
	while True:
		screen.fill(black)		

		font = pygame.font.Font(pygame.font.get_default_font(),titlesize)
		label = font.render("Security key", 1, (white))
			
		screen.blit(label, (LCD_WIDTH/2-label.get_width()/2,0+10))
	
		screen.blit(img_newkey, (LCD_WIDTH/2-img_newkey.get_width()/2, LCD_HEIGHT-img_newkey.get_height()*2))
		screen.blit(img_ok, (0, LCD_HEIGHT-img_ok.get_height()))
		screen.blit(img_cancel, (LCD_WIDTH-img_cancel.get_width(), LCD_HEIGHT-img_cancel.get_height()))
	
		# Touchscreen
		for e in pygame.event.get():
			if e.type == pygame.MOUSEBUTTONDOWN:
				pos = pygame.mouse.get_pos()
				
				if img_newkey_pos.collidepoint(pos):
					key = generateKey(WifiAPkeyLenght)
				if img_ok2_pos.collidepoint(pos):
					hostapdConfig['global']['wpa_passphrase'] = key
					write_hostapdConfig('/etc/hostapd/hostapd.conf')
					saveSettings()
					reset_wlan_ap(screen)
					network_infos(screen)
					
				if img_cancel_pos.collidepoint(pos):
					hostapdConfig['global']['wpa_passphrase'] = old_key
					network_infos(screen)
		
		font = pygame.font.Font(pygame.font.get_default_font(),choicesize)
		text = str(key)
		label = font.render(text, 1, (choicecolor))		 
		screen.blit(label, (LCD_WIDTH/2-label.get_width()/2,50))
		
		# font = pygame.font.Font(pygame.font.get_default_font(),choicesize)
		# text = str(newkey)
		# label = font.render(text, 1, (choicecolor))					 
		# screen.blit(label, (LCD_WIDTH/2-label.get_width()/2,70))
				
		pygame.display.flip()
	
def tor_country_settings(screen, title="TOR country settings", titlesize=22, choicesize = 14, statussize = 18, titlecolor=(255,255,255), choicecolor=(255,255,255), statuscolor=(255,0,0)):	
	global menupos
	global countryForced
	global countryBlocked
	menupos = 0
	x = len(countryData)-1
	y = len(countrystateData)-1
	statepos = 0
	
	while True:
		status = ""
		
		screen.fill(black)
		
		font = pygame.font.Font(pygame.font.get_default_font(),titlesize)
		label = font.render(title, 1, (titlecolor))
		
		
		screen.blit(label, (LCD_WIDTH/2-label.get_width()/2,0+10))
		
		# print countryData[menupos]
			
		screen.blit(img_left, (m2_xy[0][0], m2_xy[0][1]))
		screen.blit(img_right, (m2_xy[1][0], m2_xy[1][1]))
		
		screen.blit(img_left, (m2_xy[2][0], m2_xy[2][1]))
		screen.blit(img_right, (m2_xy[3][0], m2_xy[3][1]))
	
		screen.blit(img_ok, (LCD_WIDTH/2-img_ok.get_width()/2, LCD_HEIGHT-img_ok.get_height()))
#		screen.blit(img_cancel, (LCD_WIDTH-img_cancel.get_width(), LCD_HEIGHT-img_cancel.get_height()))

		if countryData[menupos][1] in countryForced:
			status = "Forced"
		elif countryData[menupos][1] in countryBlocked:
			status = "Blocked"
		else:
			status = "Normal"
	
		# Touchscreen
		for e in pygame.event.get():
			if e.type == pygame.MOUSEBUTTONDOWN:
				pos = pygame.mouse.get_pos()
							
				if m2_left1_pos.collidepoint(pos):	
					if menupos == 0:
						menupos = x
					else:
						menupos = menupos-1
					statepos = 0
									
#					debug_msg(menupos)
						
				if m2_right1_pos.collidepoint(pos):
					if menupos == x:
						menupos = 0
					else:					
						menupos = menupos+1
					statepos = 0
					
#					debug_msg(menupos)

				if m2_left2_pos.collidepoint(pos):	
					if statepos == 0:
						statepos = y
					else:
						statepos = statepos-1

					if statepos == 0:
						try:
							countryForced.remove(countryData[menupos][1])
						except:
							print("not in countryForced list")
						try:
							countryBlocked.remove(countryData[menupos][1])
						except:
							print("not in countryBlocked list")
							
					elif statepos == 1:
						try:
							countryForced.append(countryData[menupos][1])
						except:
							print("not in countryForced list")
						try:
							countryBlocked.remove(countryData[menupos][1])
						except:
							print("not in countryBlocked list")
							
					elif statepos == 2:
						try:
							countryForced.remove(countryData[menupos][1])
						except:
							print("not in countryForced list")
						try:
							countryBlocked.append(countryData[menupos][1])
						except:
							print("not in countryBlocked list")
		#			debug_msg(menupos)
						
				if m2_right2_pos.collidepoint(pos):
					if statepos == y:
						statepos = 0
					else:					
						statepos = statepos+1
						
					if statepos == 0:
						try:
							countryForced.remove(countryData[menupos][1])
						except:
							print("not in countryForced list")
						try:
							countryBlocked.remove(countryData[menupos][1])
						except:
							print("not in countryBlocked list")
							
					elif statepos == 1:
						try:
							countryForced.append(countryData[menupos][1])
						except:
							print("not in countryForced list")
						try:
							countryBlocked.remove(countryData[menupos][1])
						except:
							print("not in countryBlocked list")
							
					elif statepos == 2:
						try:
							countryForced.remove(countryData[menupos][1])
						except:
							print("not in countryForced list")
						try:
							countryBlocked.append(countryData[menupos][1])
						except:
							print("not in countryBlocked list")

#					debug_msg(menupos)

						
				if img_ok_pos.collidepoint(pos):
#					debug_msg("ok")
#					debug_msg(menupos)

					torrc_write(countryForced, countryBlocked, '/etc/tor/torrc')
					
					return menupos
					break
					
					
#				if img_cancel_pos.collidepoint(pos):
#					print"cancel"
		
						
				print ("countryForced : "+str(countryForced))
				print ("countryBlocked : "+str(countryBlocked))
				
		### Country	
		text = str(countryData[menupos][0])
		font = pygame.font.Font(pygame.font.get_default_font(),choicesize)
		label = font.render(text, 1, (choicecolor))
		
		# screen.blit(label, (LCD_WIDTH/2-label.get_width()/2,LCD_HEIGHT/2-font.get_height()/2))
		screen.blit(label, (LCD_WIDTH/2-label.get_width()/2,LCD_HEIGHT/4-font.get_height()/2))
		
		### Mode
		text = str(countrystateData[statepos])
		font = pygame.font.Font(pygame.font.get_default_font(),choicesize)
		label = font.render(text, 1, (choicecolor))
					 
		screen.blit(label, (LCD_WIDTH/2-label.get_width()/2,LCD_HEIGHT/2-font.get_height()/2))
		
		### Status
		text = str(status)
		font = pygame.font.Font(pygame.font.get_default_font(),statussize)
		label = font.render(text, 1, (statuscolor))
					 
		screen.blit(label, (LCD_WIDTH/2-label.get_width()/2,LCD_HEIGHT/2+40-font.get_height()/2))
		
		
				
		pygame.display.flip()		

loadSettings()				

hostapdConfig = ParseINI('/etc/hostapd/hostapd.conf')
if WifiAPkeyChangeonStartup == True:
	key = generateKey(WifiAPkeyLenght)
	hostapdConfig['global']['wpa_passphrase'] = key
	write_hostapdConfig('/etc/hostapd/hostapd.conf')
	reset_wlan_ap(screen)
	
### MAIN LOOP - START
network_infos(screen)


