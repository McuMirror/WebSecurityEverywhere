#! /usr/bin/env python
# -*- coding: utf-8 -*-

import io
import os
import pygame
import sys
from pygame.locals import *
import data
from data import *

# Initialization -----------------------------------------------------------

# Init framebuffer/touchscreen environment variables
os.environ["SDL_FBDEV"] = "/dev/fb1"
os.environ["SDL_VIDEO_CENTERED"] = "1"
os.environ["SDL_MOUSEDRV"] = "TSLIB"
os.environ["SDL_MOUSEDEV"] = "/dev/input/touchscreen"

script_old = "unjailpi_mini_5_8"
script_new = "unjailpi_mini_5_9"

# Init pygame and screen
print "Initting..."
pygame.init()
print "Setting Mouse invisible..."
pygame.mouse.set_visible(False)
print "Setting fullscreen..."
modes = pygame.display.list_modes(16)
screen = pygame.display.set_mode(modes[0], FULLSCREEN, 16)

# font
FONT = "fonts/monofonto2.ttf"

menupos = 0

def unjailpi():
	os.system('sudo python /home/pi/scripts/pygame/'+script_old+'/start.py &')
	raise SystemExit
	
def unjailpi_dev():
	os.system('sudo python /home/pi/scripts/pygame/'+script_new+'/start.py &')
	raise SystemExit

def pi_cam():	
	os.system('sudo sh /home/pi/scripts/misc/exec_picam2.sh &')
	raise SystemExit
	
def Reboot(screen):
	os.system('sudo reboot &')
	sys.exit
	
	
def Shutdown(screen):
	os.system('sudo halt &')
	sys.exit
	
	
def menu0(screen, options, title, titlesize=22, choicesize = 18, titlecolor=(255,255,255), choicecolor=(255,0,0)):	
	global menupos
	x = len(options)-1
	
	while True:
		screen.fill(black)
		
		font = pygame.font.Font(filepath(FONT), titlesize)
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
					print menupos,x
						
				if m1_right_pos.collidepoint(pos):
					if menupos == x:
						menupos = 0
					else:					
						menupos = menupos+1
					print menupos,x
						
				if img_ok_pos.collidepoint(pos):
					print "ok"
					return str(options[menupos])
					
#				if img_cancel_pos.collidepoint(pos):
#					print"cancel"
		
		text = str(options[menupos])
		font = pygame.font.Font(filepath(FONT), choicesize)
		label = font.render(text, 1, (choicecolor))
					 
		screen.blit(label, (LCD_WIDTH/2-label.get_width()/2,LCD_HEIGHT/2-font.get_height()/2))
				
		pygame.display.flip()


# load pictures
img_left = pygame.image.load(data.filepath("icons/left_s.png"))			# 48x48
img_right = pygame.image.load(data.filepath("icons/right_s.png"))		# 48x48
img_ok = pygame.image.load(data.filepath("icons/ok.png"))				# 140x60
img_cancel = pygame.image.load(data.filepath("icons/cancel.png"))		# 140x60

# this ugly variable will store arrows positions in pratical form for later use
m1_xy =  [[0, LCD_HEIGHT/2-img_left.get_height()/2], 
			[LCD_WIDTH-img_right.get_width(), LCD_HEIGHT/2-img_right.get_height()/2]]
# here is an example
m1_left_pos = pygame.Rect(m1_xy[0][0], m1_xy[0][1], img_left.get_width(), img_left.get_height())
m1_right_pos = pygame.Rect(m1_xy[1][0], m1_xy[1][1], img_right.get_width(), img_right.get_height())

img_ok_pos = pygame.Rect(LCD_WIDTH/2-img_ok.get_width()/2, LCD_HEIGHT-img_ok.get_height(), img_ok.get_width(), img_ok.get_height())
img_cancel_pos = pygame.Rect(LCD_WIDTH-img_cancel.get_width(), LCD_HEIGHT-img_cancel.get_height(), img_cancel.get_width(), img_cancel.get_height())
		
while True:
	choice = menu0(screen, [
		'UnJailPi', 
		'UnJailPi Dev', 
		'Pi-cam', 
		'Exit',
		'Reboot',
		'Shutdown'],
		'MENU')
		
	if choice == 'UnJailPi' : unjailpi()
	if choice == 'UnJailPi Dev' : unjailpi_dev()
	if choice == 'Pi-cam' : pi_cam()
	if choice == 'Reboot' : Reboot(screen)
	if choice == 'Shutdown' : Shutdown(screen)
	if choice == 'Exit' : 
#		os.system('sudo python /home/pi/scripts/pygame/bootmenu.py &')
		raise SystemExit
	pygame.display.flip()
