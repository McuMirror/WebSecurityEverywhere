import pygame, sys, os

data_py = os.path.abspath(os.path.dirname(__file__))
data_dir = os.path.normpath(os.path.join(data_py, '..', 'data'))

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

### Misc ###
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



