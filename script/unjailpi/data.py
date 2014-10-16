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

debug = False

board_type = "rpi"		# 1= rpi, 2= bpi
upis = False

WifiAPkeyLenght = '128'
WifiAPkeyChangeonStartup = True

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

mainmenuData = ['Network',
				'Settings',
				'Misc',
				'System',
				'Back'
			]
			
networkmenuData = ['Reset WiFi AP',
				'Reset WiFi Client',
				'Reset Ethernet',
				'TOR settings',
				'new AP key',
				'Back'
			]
			
settingsmenuData = ['Screen Timeout',
				'Back'
			]
			
miscmenuData = ['Power',
				'Back'
			]
			
systemmenuData = ['Menu',
				'Console',
				'Reboot',
				'Halt',
				'Back'
			]
			
displayDelayData = [0, 5, 10, 15, 30, 60, 120, 240]

countryData = [("ASCENSION ISLAND","ac"),
("AFGHANISTAN","af"),
("ALAND","ax"),
("ALBANIA","al"),
("ALGERIA","dz"),
("ANDORRA","ad"),
("ANGOLA","ao"),
("ANGUILLA","ai"),
("ANTARCTICA","aq"),
("ANTIGUA & BARBUDA","ag"),
("ARGENTINA REPUBLIC","ar"),
("ARMENIA","am"),
("ARUBA","aw"),
("AUSTRALIA","au"),
("AUSTRIA","at"),
("AZERBAIJAN","az"),
("BAHAMAS","bs"),
("BAHRAIN","bh"),
("BANGLADESH","bd"),
("BARBADOS","bb"),
("BELARUS","by"),
("BELGIUM","be"),
("BELIZE","bz"),
("BENIN","bj"),
("BERMUDA","bm"),
("BHUTAN","bt"),
("BOLIVIA","bo"),
("BOSNIA & HERZEGOVINA","ba"),
("BOTSWANA","bw"),
("BOUVET ISLAND","bv"),
("BRAZIL","br"),
("BRITISH INDIAN OCEAN TERR","io"),
("BRITISH VIRGIN ISLANDS","vg"),
("BRUNEI DARUSSALAM","bn"),
("BULGARIA","bg"),
("BURKINA FASO","bf"),
("BURUNDI","bi"),
("CAMBODIA","kh"),
("CAMEROON","cm"),
("CANADA","ca"),
("CAPE VERDE","cv"),
("CAYMAN ISLANDS","ky"),
("CENTRAL AFRICAN REPUBLIC","cf"),
("CHAD","td"),
("CHILE","cl"),
("CHINA","cn"),
("CHRISTMAS ISLANDS","cx"),
("COCOS ISLANDS","cc"),
("COLOMBIA","co"),
("COMORAS","km"),
("CONGO","cg"),
("CONGO DEMOCRATIC REPUBLIC","cd"),
("COOK ISLANDS","ck"),
("COSTA RICA","cr"),
("COTE D IVOIRE","ci"),
("CROATIA","hr"),
("CUBA","cu"),
("CYPRUS","cy"),
("CZECH REPUBLIC","cz"),
("DENMARK","dk"),
("DJIBOUTI","dj"),
("DOMINICA","dm"),
("DOMINICAN REPUBLIC","do"),
("EAST TIMOR","tp"),
("ECUADOR","ec"),
("EGYPT","eg"),
("EL SALVADOR","sv"),
("EQUATORIAL GUINEA","gq"),
("ESTONIA","ee"),
("ETHIOPIA","et"),
("FALKLAND ISLANDS","fk"),
("FAROE ISLANDS","fo"),
("FIJI","fj"),
("FINLAND","fi"),
("FRANCE","fr"),
("FRANCE METROPOLITAN","fx"),
("FRENCH GUIANA","gf"),
("FRENCH POLYNESIA","pf"),
("FRENCH SOUTHERN TERRITORIES","tf"),
("GABON","ga"),
("GAMBIA","gm"),
("GEORGIA","ge"),
("GERMANY","de"),
("GHANA","gh"),
("GIBRALTER","gi"),
("GREECE","gr"),
("GREENLAND","gl"),
("GRENADA","gd"),
("GUADELOUPE","gp"),
("GUAM","gu"),
("GUATEMALA","gt"),
("GUINEA","gn"),
("GUINEA-BISSAU","gw"),
("GUYANA","gy"),
("HAITI","ht"),
("HEARD & MCDONALD ISLAND","hm"),
("HONDURAS","hn"),
("HONG KONG","hk"),
("HUNGARY","hu"),
("ICELAND","is"),
("INDIA","in"),
("INDONESIA","id"),
("IRAN, ISLAMIC REPUBLIC OF","ir"),
("IRAQ","iq"),
("IRELAND","ie"),
("ISLE OF MAN","im"),
("ISRAEL","il"),
("ITALY","it"),
("JAMAICA","jm"),
("JAPAN","jp"),
("JORDAN","jo"),
("KAZAKHSTAN","kz"),
("KENYA","ke"),
("KIRIBATI","ki"),
("KOREA - DEM. PEOPLES REP OF","kp"),
("KOREA - REPUBLIC OF","kr"),
("KUWAIT","kw"),
("KYRGYZSTAN","kg"),
("LAO PEOPLES DEM. REPUBLIC","la"),
("LATVIA","lv"),
("LEBANON","lb"),
("LESOTHO","ls"),
("LIBERIA","lr"),
("LIBYAN ARAB JAMAHIRIYA","ly"),
("LIECHTENSTEIN","li"),
("LITHUANIA","lt"),
("LUXEMBOURG","lu"),
("MACAO","mo"),
("MACEDONIA","mk"),
("MADAGASCAR","mg"),
("MALAWI","mw"),
("MALAYSIA","my"),
("MALDIVES","mv"),
("MALI","ml"),
("MALTA","mt"),
("MARSHALL ISLANDS","mh"),
("MARTINIQUE","mq"),
("MAURITANIA","mr"),
("MAURITIUS","mu"),
("MAYOTTE","yt"),
("MEXICO","mx"),
("MICRONESIA","fm"),
("MOLDAVA","md"),
("MONACO","mc"),
("MONGOLIA","mn"),
("MONTENEGRO","me"),
("MONTSERRAT","ms"),
("MOROCCO","ma"),
("MOZAMBIQUE","mz"),
("MYANMAR","mm"),
("NAMIBIA","na"),
("NAURU","nr"),
("NEPAL","np"),
("NETHERLANDS ANTILLES","an"),
("NETHERLANDS","nl"),
("NEW CALEDONIA","nc"),
("NEW ZEALAND","nz"),
("NICARAGUA","ni"),
("NIGER","ne"),
("NIGERIA","ng"),
("NIUE","nu"),
("NORFOLK ISLAND","nf"),
("NORTHERN MARIANA ISLANDS","mp"),
("NORWAY","no"),
("OMAN","om"),
("PAKISTAN","pk"),
("PALAU","pw"),
("PALESTINE","ps"),
("PANAMA","pa"),
("PAPUA NEW GUINEA","pg"),
("PARAGUAY","py"),
("PERU","pe"),
("PHILIPPINES","ph"),
("PITCAIRN","pn"),
("POLAND","pl"),
("PORTUGAL","pt"),
("PUERTO RICO","pr"),
("QATAR","qa"),
("REUNION","re"),
("ROMANIA","ro"),
("RUSSIAN FEDERATION","ru"),
("RWANDA","rw"),
("SAMOA","ws"),
("SAN MARINO","sm"),
("SAO TOME - PRINCIPE","st"),
("SAUDI ARABIA","sa"),
("SCOTLAND","uk"),
("SENEGAL","sn"),
("SERBIA","rs"),
("SEYCHELLES","sc"),
("SIERRA LEONE","sl"),
("SINGAPORE","sg"),
("SLOVAKIA","sk"),
("SLOVENIA","si"),
("SOLOMON ISLANDS","sb"),
("SOMALIA","so"),
("SOMOA, GILBERT - ELLICE ISLANDS","as"),
("SOUTH AFRICA","za"),
("SOUTH SANDWICH ISLANDS","gs"),
("SOVIET UNION","su"),
("SPAIN","es"),
("SRI LANKA","lk"),
("ST. HELENA","sh"),
("ST. KITTS & NEVIS","kn"),
("ST. LUCIA","lc"),
("ST. PIERRE & MIQUELON","pm"),
("ST. VINCENT & THE GRENADINES","vc"),
("SUDAN","sd"),
("SURINAME","sr"),
("SVALBARD & JAN MAYEN","sj"),
("SWAZILAND","sz"),
("SWEDEN","se"),
("SWITZERLAND","ch"),
("SYRIAN ARAB REPUBLIC","sy"),
("TAIWAN","tw"),
("TAJIKISTAN","tj"),
("TANZANIA - UNITED REPUBLIC OF","tz"),
("THAILAND","th"),
("TOGO","tg"),
("TOKELAU","tk"),
("TONGA","to"),
("TRINIDAD & TOBAGO","tt"),
("TUNISIA","tn"),
("TURKEY","tr"),
("TURKMENISTAN","tm"),
("TURKS & CALCOS ISLANDS","tc"),
("TUVALU","tv"),
("UGANDA","ug"),
("UKRAINE","ua"),
("UNITED ARAB EMIRATES","ae"),
("UNITED KINGDOM - OLD","gb"),
("UNITED KINGDOM","uk"),
("UNITED STATES","us"),
("UNITED STATES MINOR OUTL.IS.","um"),
("URUGUAY","uy"),
("UZBEKISTAN","uz"),
("VANUATU","vu"),
("VATICAN CITY STATE","va"),
("VENEZUELA","ve"),
("VIET NAM","vn"),
("VIRGIN ISLANDS","vi"),
("WALLIS & FUTUNA ISLANDS","wf"),
("WESTERN SAHARA","eh"),
("YEMEN","ye"),
("ZAMBIA","zm"),
("ZIMBABWE","zw")]

# https://anonymous-proxy-servers.net/wiki/index.php/Censorship-free_DNS_servers
# http://www.coyotus.com/viewtopic.php?id=658
# http://www.backtrack-linux.org/forums/showthread.php?t=1496
DNSData = [("Chaos Computer Club Berlin","213.73.91.35"),
("Comodo Secure DNS #1","156.154.70.22"),
("Comodo Secure DNS #2","156.154.71.22"),
("Censurfridns (Denmark) #1","89.233.43.71"),
("Censurfridns (Denmark) #2","89.104.194.142"),
("DNS Advantage #1","156.154.70.1"),
("DNS Advantage #2","156.154.71.1"),
("Dotplex #1","91.102.11.144"),
("Dotplex #2","212.222.128.86"),
("FoeBuD e.V.","85.214.20.141"),
("Schweden DNS Kalmar NDC Registry","213.132.114.4"),
("Island DNS Island Telecom","213.167.155.16"),
("Antartica DNS (Cyberbunker NL)","84.22.106.30"),
("US DNS Westelcom Internet, Inc.","64.19.76.8")
]

countrystateData = ['Normal',
				'Forced',
				'Blocked']
				
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
