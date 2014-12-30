#!/usr/bin/python
import pygame
import sys
import os 
import time
import tftutils
import fmu
import camera

os.environ["SDL_FBDEV"] = "/dev/fb1"

#
# TFT Class
# main pygame screen, app class
#  	
class TFT:
	
	def __init__(self):
		pygame.init()
		pygame.mouse.set_visible(False)
		pygame.display.set_caption('Basic Pygame program')
		
		self.menu_color = (241, 66, 198)
		self.highlight_color = (139, 250, 73)
		self.menu_bg_color = (60,44,28)
		self.scroll_color = (246,248,63)
		self.other_btn_color = (52,178,237)
		self.other_btn_highlight_color = (249, 176, 72)
		
		
		self.app_state = 0
		self.menu_state = 0
		
		self.screen_size = (160,128)
		self.screen = pygame.display.set_mode(self.screen_size, 0, 32)
		self.background = pygame.Surface(self.screen_size)
		self.background.convert()
		
		self.menu_font_size = 16
		self.menu_line_height = 17
		self.menu_font = pygame.font.Font('/home/pi/fonts/FUTURA_N.TTF', self.menu_font_size) 
		self.menu = pygame.Surface(self.screen_size)
		self.menu_updated = True
		
		self.fmu = fmu.FMUApp(self.screen_size, self.menu_color, self.highlight_color, self.menu_bg_color, self.scroll_color, self.other_btn_color, self.other_btn_highlight_color)
		self.camera = camera.CameraApp(self.screen_size, self.menu_color, self.highlight_color, self.menu_bg_color)
		
		self.menu_array = [
			{'title':'FMU', 'app':self.fmu},
			{'title':'PiCamera', 'app':self.camera}
		]
		
		self.current_app = None
		
		self.btns = tftutils.BTNS()
		self.btns.change += self.on_button_change
		
		self.screensaver = tftutils.TFTScreensaver((0,0), self.screen_size)
		self.screensaver_on = False
		self.screensaver.fire += self.on_screensaver_fire
		self.screensaver_on = False
		self.screensaver.start()
		
		self.update_menu()
		
	def on_screensaver_fire(self):
		self.screensaver_on = True
		
	def on_button_change(self, dir):
		self.screensaver.reset()
		if self.screensaver_on == True:
			self.menu_updated = True
			self.screensaver_on = False
			return
		if self.app_state == 0:
			
			app = self.app_state
			menu = self.menu_state
			
			if dir == 'up':
				self.set_states(app,menu - 1)
			elif dir == 'down':
				self.set_states(app,menu + 1)
			elif dir == 'center':
				self.set_states(1,menu)
			
		else:	
			self.current_app.on_button_change(dir)
	
	def set_states(self, app, menu):
		if app > 1:
			app = 0
		elif app < 0:
			app = 1
		
		menu_max = len(self.menu_array) - 1
		if menu > menu_max:
			menu = 0
		elif menu < 0:
			menu = menu_max
			
		self.app_state = app
		self.menu_state = menu
	
		if self.app_state == 1:
			self.start_current_app()
		else:
			self.update_menu()
	
	def start_current_app(self):
		self.current_app = self.menu_array[self.menu_state]['app']
		self.current_app.exit += self.on_app_exit
		self.current_app.start_app()
		self.menu_state = 0
		self.update_screensaver()
	
	def on_app_exit(self):
		self.current_app.exit -= self.on_app_exit
		self.current_app = None
		self.set_states(0,self.menu_state)
		self.update_screensaver()
		
	def update_screensaver(self):
		if(self.current_app == self.fmu):
			self.screensaver.update_size((0, 30), (self.screen_size[0], self.screen_size[1] - 30))
		else:
			self.screensaver.update_size((0, 0), self.screen_size )
		
	def update_menu(self):
		self.menu.fill(self.menu_bg_color)
		self.render_menu()
		
	def render_menu(self):
		ypos = 20
		for i in range( len( self.menu_array )):
			option_name = self.menu_array[i]['title']
			if i == self.menu_state:
				self.menu.fill((0,0,0), (0, ypos, 160, self.menu_line_height ))
				sur = self.menu_font.render(option_name, 1, self.highlight_color)
			else:
				sur = self.menu_font.render(option_name, 1, self.menu_color)
			self.menu.blit( sur, (5, ypos) )
			ypos = ypos + self.menu_line_height
			
		self.menu_updated = True
		
	def update_surface(self):
		#self.background.fill((10, 10, 10))
		if self.screensaver_on == False:
			if self.app_state == 0:
				if self.menu_updated == True:
					self.background.blit(self.menu, (0,0))
					self.menu_updated = False
			else:
				current_app = self.menu_array[self.menu_state]
				self.background.blit(self.current_app.update_surface(), [0,0])
		else:
			if self.current_app == self.fmu:
				self.background.blit(self.current_app.update_surface(), [0,0])
			self.screensaver.update_surface()
			self.background.blit(self.screensaver.surface, self.screensaver.origin)
		
		self.screen.blit(self.background, (0, 0))
		pygame.display.flip()
	
	def close(self):
		pygame.quit()
		sys.exit()
		
	def run(self):
		while True:
			try:
				for event in pygame.event.get():
					if event.type == QUIT:
						self.close()
				self.update_surface()
				time.sleep(.005)
			except KeyboardInterrupt:
				self.close()

if __name__ == "__main__" :
    game = TFT()
    game.run()