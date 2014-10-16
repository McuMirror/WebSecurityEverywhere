#! /usr/bin/env python
# -*- coding: utf-8 -*-

##########################
#Autonomous internet security box
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

import pygame, sys, os
import threading
import subprocess
from pygame.locals import *
import time
from time import sleep
import datetime
import math

# find process
import re

data_py = os.path.abspath(os.path.dirname(__file__))
data_dir = os.path.normpath(os.path.join(data_py, '..', 'data'))

## // --> config.py
popup_border = 5

debug = True

board_type = "rpi"		# 1= rpi, 2= bpi

## config.py --> //

# couleurs
red = (255,0,0)
green = (0,255,0)
blue = (0,0,255)
darkBlue = (0,0,128)
white = (255,255,255)
black = (0,0,0)
pink = (255,200,200)
yellow = (255,255,0)

LCD_WIDTH = 320
LCD_HEIGHT = 240

SPACE = 0

### Wireless ###
WLAN_AP = "wlan0"			# access point interface
WLAN_CLIENT = "wlan1"		# client interface

BACK_PICTURE = "overlay.png"
template_PICTURE = "page1_320x240.png"

NETWORKMAIN_ICONSIZE = 32
TOPBAR_ICONSIZE = 16
MISC_ICONSIZE = 48
BOTTOMBAR_ICONSIZE = 48
BOTTOMBAR_TOR_OFF = "tor_off.png"
BOTTOMBAR_TOR_ON = "tor_on.png"
BOTTOMBAR_VPN_OFF = "vpn_off.png"
BOTTOMBAR_VPN_ON = "vpn_on.png"
BOTTOMBAR_MENU = "menu_btn.png"

### Fonts ###
# MAIN_FONT = "fonts/font.ttf"
MAIN_FONT = "fonts/monofonto2.ttf"
TOPBAR_FONT = "fonts/monofonto2.ttf"
CLOCK_FONT = "fonts/monofonto2.ttf"
POPUP_FONT = "fonts/coders_crux.ttf"

# MAIN_FONTSIZE = 8
MAIN_FONTSIZE = 12
PAGETITLE_FONTSIZE = 24
TOPBAR_FONTSIZE = 10
CLOCK_FONTSIZE = 14
POPUP_FONTSIZE = 22

MARGIN_X = 10
MARGIN_Y = 12

BACK_COLOR = None

MAIN_FONTCOLOR = white
PAGETITLE_FONTCOLOR = red
CLOCK_FONTCOLOR = green

POPUP_FONTCOLOR = black
POPUP_BGCOLOR = red

### Icons ###
NETWORK_INTON = "internet_on.png"
NETWORK_INTOFF = "internet_off.png"
NETWORK_INTTOR = "tor.png"
NETWORK_INTVPN = "gpg.png"
NETWORK_CLION = "wifi_on.png"
NETWORK_CLIOFF = "wifi_off.png"

TOPBAR_APON = "remote_on.png"
TOPBAR_APOFF = "remote_off.png"
TOPBAR_CLION = "wifi_on.png"
TOPBAR_CLIOFF = "wifi_off.png"
TOPBAR_ETHON = "LAN_on.png"
TOPBAR_ETHOFF = "LAN_off.png"
TOPBAR_USB = "usb.png"
TOPBAR_TOR = "tor.png"
TOPBAR_OVERTEMP = "temperature-5-icon_2.png"

### Misc ###
GET_EXTIP_DELAY = 15
GET_EXTIP_TIMEOUT = 10
GET_IP_DELAY = 5
GET_ESSID_DELAY = 5
GET_CPUTEMP_DELAY = 5
GET_LOAD_AVERAGE_DELAY = 5
GET_UPTIME_DELAY = 30
GET_CPU_USAGE_DELAY = 10
GET_WLANQUALITY_DELAY = 3
GET_UPIS_DELAY = 20
GET_UPIS_TMP_DELAY = 10

UPIS_TEMP_ALERT = 55

REFRESH_RATE = 250

GET_IP_METHOD = 2

def debug_msg(msg):
	if debug == True:
		print str(msg)

def Reboot(screen):
	screen.fill((0, 0, 0))
	font = pygame.font.Font(filepath("fonts/coders_crux.ttf"), 32)
	label = font.render("REDEMARRAGE", 1, (red))
	screen.blit(label, (64-label.get_width()/2, 80-font.get_height()/2))
	pygame.display.flip()
	sys.exit
	os.system('sudo reboot')
	
def Shutdown(screen):
	screen.fill((0, 0, 0))
	font = pygame.font.Font(filepath("fonts/coders_crux.ttf"), 32)
	label = font.render("EXTINCTION", 1, (red))
	screen.blit(label, (64-label.get_width()/2, 80-font.get_height()/2))
	pygame.display.flip()
	sys.exit
	os.system('sudo halt')

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

# def show_popup_new(screen, text):
	# font = pygame.font.Font(None, 20)
	# label = font.render(text, 1, (yellow))
	# label_x = (LCD_WIDTH/2)-(label.get_width()/2)
	# label_y = (LCD_HEIGHT/2)-(font.get_height()/2)
	# pygame.draw.rect(screen, red, (label_x, label_y, 20,40), 0)
	# screen.blit(label, (label_x, label_y))		
	# rotated = pygame.transform.rotate(screen, 90)
	# screen.blit(rotated, (0, 0))
	# pygame.display.flip()
	
def show_popup(screen, text):
	font = pygame.font.Font(filepath(POPUP_FONT), POPUP_FONTSIZE)
	label = font.render(text, 1, (POPUP_FONTCOLOR))
	pygame.draw.rect(screen, POPUP_BGCOLOR, (LCD_WIDTH/2-label.get_width()/2-popup_border, LCD_HEIGHT/2-font.get_height()/2-popup_border, label.get_width()+popup_border*2,font.get_height()+popup_border*2,), 0)
	screen.blit(label, (LCD_WIDTH/2-label.get_width()/2, LCD_HEIGHT/2-font.get_height()/2))
	pygame.display.flip()
	

class MyTimer:
    def __init__(self, tempo, target, args= [], kwargs={}):
        self._target = target
        self._args = args
        self._kwargs = kwargs
        self._tempo = tempo

    def _run(self):
        self._timer = threading.Timer(self._tempo, self._run)
        self._timer.start()
        self._target(*self._args, **self._kwargs)
        
    def start(self):
        self._timer = threading.Timer(self._tempo, self._run)
        self._timer.start()

    def stop(self):
        self._timer.cancel()

def read_cpu_temp():
	global cputemp	
	if board_type == "rpi":		# RPi
		res = os.popen('vcgencmd measure_temp').readline()
		cputemp = res.replace("temp=","").replace("'C\n","")
	if board_type == "bpi":		# BPi
		cmd = """cat /sys/devices/platform/sunxi-i2c.0/i2c-0/0-0034/temp1_input |awk '{printf ("%0.1f",$1/1000); }'"""
		cputemp = os.popen(cmd).readline().strip()
	debug_msg("CPU - TEMP : "+cputemp+"")
	return(cputemp)
	
def read_cpu_usage():
	global cpu_usage
	cpu_usage = format(psutil.cpu_percent())
	debug_msg("CPU - USAGE : "+cpu_usage+"")
	return(cpu_usage)
	
def read_load_average():
	global load_average
	s = subprocess.check_output(["uptime"])
	load_split = s.split("load average: ")
	load_average = format(float(load_split[1].split(',')[1]))
	debug_msg("LOAD - AVERAGE : "+load_average+"")
	return (load_average)
	
def read_uptime():
	global uptime
	s = subprocess.check_output(["uptime"])
	load_split = s.split("load average: ")
	up = load_split[0]
	up_pos = up.rfind(',',0,len(up)-4)
	up = up[:up_pos].split('up ')[1]
	uptime = up
	debug_msg("UPTIME : "+uptime+"")
	return (uptime)
	
def get_time():
	current_time = datetime.datetime.now().time()
	now = current_time.strftime("%H:%M:%S")
	return (now)
	
def process_exists(proc_name):
    ps = subprocess.Popen("ps ax -o pid= -o args= ", shell=True, stdout=subprocess.PIPE)
    ps_pid = ps.pid
    output = ps.stdout.read()
    ps.stdout.close()
    ps.wait()

    for line in output.split("\n"):
        res = re.findall("(\d+) (.*)", line)
        if res:
            pid = int(res[0][0])
            if proc_name in res[0][1] and pid != os.getpid() and pid != ps_pid:
                return True
    return False
	
def reload_tor(screen):
	if process_exists("openvpn") == True:
			os.system('sudo nohup killall openvpn > /dev/null 2>&1 &')
	if process_exists("tor") == True:
		show_popup(screen, "Getting new internet ID")
		os.system('sudo /home/pi/scripts/tor/tor_restart.sh &')
		os.system('sudo iptables -F')
		os.system('sudo iptables -t nat -F')
		os.system('sudo iptables -t nat -A POSTROUTING -o '+WLAN_CLIENT+' -j MASQUERADE')
		os.system('sudo iptables -A FORWARD -i '+WLAN_CLIENT+' -o '+WLAN_AP+' -m state --state RELATED,ESTABLISHED -j ACCEPT')
		os.system('sudo iptables -A FORWARD -i '+WLAN_AP+' -o '+WLAN_CLIENT+' -j ACCEPT')
	else:
		show_popup(screen, "Changing internet ID")		
		os.system('sudo /home/pi/scripts/tor/tor_start.sh &')
		os.system('sudo iptables -F')
		os.system('sudo iptables -t nat -F')
		os.system('sudo iptables -t nat -A POSTROUTING -o '+WLAN_CLIENT+' -j MASQUERADE')
		os.system('sudo iptables -A FORWARD -i '+WLAN_CLIENT+' -o '+WLAN_AP+' -m state --state RELATED,ESTABLISHED -j ACCEPT')
		os.system('sudo iptables -A FORWARD -i '+WLAN_AP+' -o '+WLAN_CLIENT+' -j ACCEPT')
	
def Openvpn_Start():
	os.system('sudo nohup openvpn --config /home/pi/scripts/openvpn/raspi-secureap/client.conf	> /dev/null 2>&1 &')
	


def Openvpn_Stop():
	os.system('sudo nohup killall openvpn > /dev/null 2>&1 &')
	
def Tor_Start(screen):
	show_popup(screen, "Starting TOR")
	# os.system('sudo service tor start &')
	os.system('sudo /home/pi/scripts/tor/tor_start.sh &')
	
def Tor_Stop(screen):
	show_popup(screen, "Restoring normal IP")
	os.system('sudo service tor stop &')			

def get_iface_ip(iface):
	"Returns the IP address for the given interface e.g. eth0"	
	if os.path.exists('/sys/class/net/'+iface):
		try:
			s = subprocess.check_output(["ip","addr","show",iface])
			ip = s.split('\n')[2].strip().split(' ')[1].split('/')[0]
			field = ip
			debug_msg("NETWORK - "+iface+" : "+field+"")
			return field
		except:
			field = "Not connected"
			debug_msg("NETWORK - "+iface+" : "+field+"")
			return field
	else:
		field = "Not found"	
		debug_msg("NETWORK - "+iface+" : "+field+"")
		return field

def torrc_write(countryForced, countryBlocked, file):
	data = "Log notice file /var/log/tor/notices.log\n"
	data += "VirtualAddrNetwork 10.192.0.0/10\n"
	data += "AutomapHostsSuffixes .onion,.exit\n"
	data += "AutomapHostsOnResolve 1\n"
	data += "TransPort 9040\n"
	data += "TransListenAddress 127.0.0.1\n"
	data += "TransListenAddress 192.168.200.1\n"
	data += "DNSPort 53\n"
	data += "DNSListenAddress 127.0.0.1\n"
	data += "DNSListenAddress 192.168.200.1\n"
	data += "AvoidDiskWrites 1\n"
	data += "ControlPort 9051\n"

	data += "StrictExitNodes 1"

	f = open(file, 'wb')
	f.write(data+"\n")
	
	f.write("ExitNodes ")
	for countrycode in countryForced:
		f.write("{"+countrycode+"},")
	f.write("\n")
	
	f.write("ExcludeExitNodes ")
	for countrycode in countryBlocked:
		f.write("{"+countrycode+"},")
	f.write("\n")
	f.close()
