#!/usr/bin/python
import pygame
import sys
import os 
import time
import urllib
import re
import feedparser
import thread
import subprocess
import random
#from subprocess import *
#from pygame.locals import *
import RPi.GPIO as GPIO 
GPIO.setmode(GPIO.BCM)

os.environ["SDL_FBDEV"] = "/dev/fb1"

#
# EventHook Class
#
class EventHook(object):
	def __init__(self):
		self.__handlers = []

	def __iadd__(self, handler):
		self.__handlers.append(handler)
		return self

	def __isub__(self, handler):
		self.__handlers.remove(handler)
		return self

	def fire(self, *args, **keywargs):
		for handler in self.__handlers:
			handler(*args, **keywargs)

#
# TFTApp Class
#
class TFTApp:
	def __init__(self, size):
		self.app_states = [0]
		self.menu_states = [0]
		self.app_state = self.app_states[0]
		self.menu_state = self.menu_states[0]
		
	def isValidAppState(state):
		if state in self.app_states:
			return true
		return false
		
	def isValidMenuState(state):
		if state in self.menu_states:
			return true
		return false
		
	def gotoNextMenuState(self):
		pass
	
	def gotoNextAppState(self):
		pass
		
	def gotoAppState(self, state):
		if self.isValidAppState(state):
			return
		
	def gotoMenuState(self, state):
		if self.isValidMenuState(state):
			return
	
	def exit_app(self):
		pass

#
# CameraApp
#
class CameraApp():
	def __init__(self, size):
		
		self.menu_color = (241, 66, 198)
		self.highlight_color = (249,240,97)
		self.menu_bg_color = (60,44,28)
		
		self.app_state = 0
		self.menu_state = 0
		
		self.size = (160,128)

		self.menu_font_size = 16
		self.menu_line_height = 17
		self.menu_font = pygame.font.Font('/home/pi/fonts/FUTURA_N.TTF', self.menu_font_size) 
		self.menu = pygame.Surface(self.size)
		self.menu_updated = True
		
		self.menu_array = [
			{'title':'shutter'}
		]
	
		self.update_menu()
	
	def on_button_change(self, dir):
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
			do_action()
		else:
			self.update_menu()
	
	def do_action(self):
		pass
	
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
		if self.app_state == 0:
			if self.menu_updated == True:
				self.surface.blit(self.menu, (0,0))
				self.menu_updated = False
		else:
			pass
			
	def start_app(self):
		pass
	
	def exit_app(self):
		pass
	
#
# FMUApp Class
# inherits from TFTApp
#
class FMUApp():#TFTApp):
	streams = [
		{'title':'WFMU','url':'http://stream0.wfmu.org/freeform-128k'}, 
		{'title':'GtDR','url':'http://stream0.wfmu.org:80/drummer'},
		{'title':'Ichiban','url':'http://stream0.wfmu.org/ichiban'},
		{'title':'Ubu','url':'http://stream0.wfmu.org/ubu'},
		{'title':'DIY','url':'http://stream0.wfmu.org/do-or-diy'}
	]
	otherStations = [
		{'title':'wnyc','url':'http://fm939.wnyc.org/wnycfm'},
		{'title':'bbc','url':'http://am820.wnyc.org/wnycam'},
		{'title':'wqxr','url':'http://stream.wqxr.org/wqxr'},
		{'title':'q2','url':'http://q2stream.wqxr.org/q2'}
	]
	controls = [
		{'title':'play_pause','url':''},
		{'title':'volume_up','url':''},
		{'title':'volume_down','url':''},
		{'title':'seek_back','url':''},
		{'title':'seek_forward','url':''},
		{'title':'exit','url':''}
	]
	functions = [
		{'title':'restart','url':''},
		{'title':'exit','url':''}
	]
	archives = []
	
	def __init__(self, size):
		#TFTApp.__init__(self, size)
		self.surface = pygame.Surface(size)
		self.menu_array = [
			{'title':'controls','tracks':FMUApp.controls},
			{'title':'streams','tracks':FMUApp.streams},
			{'title':'archives','tracks':FMUApp.archives},
			{'title':'other','tracks':FMUApp.otherStations}
			#{'title':'function','tracks':FMUApp.functions}
		]
		self.app_state = 0
		self.menu_state = 0
		self.sub_menu_state = 0
		self.back_button = False
		
		self.scroll_color = (139, 250, 73)
		self.menu_color = (241, 66, 198)
		self.highlight_color = (249,240,97)
		self.menu_bg_color = (60,44,28)
		self.back_btn_color = (52,178,237)
		self.back_highlight_color = (249, 176, 72)
		
		self.menu_height = 98
		self.menu_width = 160
		self.menu_font_size = 16
		self.menu_line_height = 17
		self.menu_font = pygame.font.Font('/home/pi/fonts/FUTURA_N.TTF', self.menu_font_size) 
		self.menu = pygame.Surface((self.menu_width, self.menu_height))
		
		self.menu_updated = False
		self.got_archives = False
		
		self.screensaver = FMUScreensaver((self.menu_width, self.menu_height))
		self.screensaver.fire += self.on_screensaver_fire
		
		self.fmu_scroll = FMUScroll(160, self.scroll_color)
		self.mpc = MPC()
		self.mpc.change += self.on_mpc_change
		
		self.url_opener = urllib.FancyURLopener({})
		
		self.exit = EventHook()
		
	def start_app(self):
		self.screensaver_on = False
		self.mpc.start()
		self.mpc.load_stream(FMUApp.streams[0]['url'])
		self.update_menu()
		self.screensaver.start()
	
	#
	# on_mpc_change
	# receives evts from MPC class
	#
	def on_mpc_change(self, evt):
		if evt['type'] == 'player':
			current = self.filter_stream_name( evt['data'][0] )
			if current != self.fmu_scroll.text:
				self.fmu_scroll.update_surface( current )
			if evt['data'][2] == True:
				self.update_menu()
		elif evt['type'] == 'mixer':
			self.update_menu()
			
	#
	# on_button_change
	# called by TFT, which receives evts BTNS class
	#
	def on_button_change(self, dir):
		self.screensaver.reset()
		if self.screensaver_on == True:
			self.screensaver_on = False
			self.update_menu()
			return
		app = self.app_state
		menu = self.menu_state
		sub = self.sub_menu_state
		if dir == 'right':
			if app == 0 and menu == 0:
				self.set_states(app,menu,sub + 1)
			elif app == 1:
				self.toggleBackButton()
		elif dir == 'left':
			if app == 0 and menu == 0:
				self.set_states(app,menu,sub - 1)
			elif app == 1:
				self.toggleBackButton()
		elif dir == 'up':
			if app == 0:
				self.set_states(app,menu - 1,0)
			else:
				self.set_states(app,menu,sub - 1)
		elif dir == 'down':
			if app == 0:
				self.set_states(app,menu + 1,0)
			else:
				self.set_states(app,menu,sub + 1)
		elif dir == 'center':
			if app == 0:
				if menu == 0:
					self.do_menu_option()
				else:
					self.set_states(1,menu,0)
			else:
				if self.back_button == True:
					self.do_back_button();
				else:	
					self.do_menu_option()
	
	#
	# set_states
	# maintain the app's state vars
	#
	def set_states(self,app,menu,sub):
		if app > 1:
			app = 0
		elif app < 0:
			app = 1
		
		menu_max = len(self.menu_array) - 1
		if menu > menu_max:
			menu = 0
		elif menu < 0:
			menu = menu_max
			
		sub_max = len( self.menu_array[ self.menu_state ][ 'tracks' ] ) - 1
		if sub > sub_max:
			sub = 0
		elif sub < 0:
			sub = sub_max
		
		self.app_state = app
		self.menu_state = menu
		self.sub_menu_state = sub
		
		#print 'FMUApp:set_states:app:' + str(app) + ' menu:' + str(menu) + ' sub:' + str(sub)
		
		self.update_menu()
	
	#
	# do_menu_option
	#
	def do_menu_option(self):
		if self.menu_state == 0:
			self.do_mpc_control()
		elif self.menu_state == 2:
			self.load_archive()
		elif self.menu_state == 4:
			self.do_function()
		else:
			self.play_track()
	
	
	def do_mpc_control(self):
		title = self.menu_array[self.menu_state]['tracks'][self.sub_menu_state]['title']
		if  title == 'play_pause':
			self.mpc.toggle_pause()
		elif title == 'volume_up':
			self.mpc.set_volume(1)
		elif title == 'volume_down':
			self.mpc.set_volume(0)
		elif title == 'seek_back':
			self.mpc.seek(0)
		elif title == 'seek_forward':
			self.mpc.seek(1)
		elif title == 'exit':
			self.exit_app()
	
	def do_function(self):
		if self.menu_array[self.menu_state]['tracks'][self.sub_menu_state]['title'] == 'restart':
			self.do_restart()
	
	def load_archive(self):
		url = self.menu_array[self.menu_state]['tracks'][self.sub_menu_state]['url']
		f = self.url_opener.open( url )
		stream = f.read()
		self.mpc.load_stream(stream)
		self.set_states(0,0,0)
		
	def play_track(self):
		url = self.menu_array[self.menu_state]['tracks'][self.sub_menu_state]['url']
		self.mpc.play_track(url)
		self.set_states(0,0,0)
	
	def do_restart(self):
		pass
	
	def exit_app(self):
		self.screensaver.stop()
		self.mpc.stop()
		self.exit.fire()
	
	#
	# update_menu
	# calls render of appropriate menu type
	#
	def update_menu(self):
		self.menu.fill(self.menu_bg_color)
		
		if self.app_state == 0:
			self.render_main_menu()
		else:
			self.render_sub_menu()
			
	#
	# render_main_menu
	#
	def render_main_menu(self):
		ypos = self.menu_line_height
		
		self.render_main_controls()
		
		for i in range( len(self.menu_array) - 1 ):
			option_name = self.menu_array[i+1]['title']
			if i + 1 == self.menu_state:
				self.menu.fill((0,0,0), (0, ypos, 160, self.menu_line_height ))
				sur = self.menu_font.render(option_name, 1, self.highlight_color)
			else:
				sur = self.menu_font.render(option_name, 1, self.menu_color)
			self.menu.blit( sur, (5, ypos) )
			ypos = ypos + self.menu_line_height
			
		self.menu_updated = True
	
	#
	#render_sub_menu
	#
	def render_sub_menu(self):
		
		if self.menu_array[self.menu_state]['title'] == 'archives' and self.got_archives == False:
			self.get_archives()
		
		options_per_page = 5
		page = int(self.sub_menu_state / options_per_page)
		active_index = self.sub_menu_state % options_per_page
		sub_menu = self.menu_array[self.menu_state]['tracks']
		slice_length = len( sub_menu[page * options_per_page:page * options_per_page + options_per_page] )
		
		for i in range(slice_length):
			
			ypos = i * self.menu_line_height
			option_name = sub_menu[page * options_per_page + i]['title']
			
			if i == active_index and self.back_button == False:
				self.menu.fill((0,0,0),(0,ypos,160, self.menu_line_height))
				sur = self.menu_font.render(option_name, 1, self.highlight_color)
			else:
				sur = self.menu_font.render(option_name, 1, self.menu_color)
			self.menu.blit( sur, (5, ypos) )
		
		self.render_sub_controls()
		
		self.menu_updated = True
	
	#
	# render mpc controls
	#
	def render_main_controls(self):
		if self.menu_state == 0:
			self.menu.fill((0,0,0),(0,0,160,self.menu_line_height))
		startx = 5
		starty = 3
		menu = self.menu_state
		color = self.menu_color
		if menu == 0 and self.sub_menu_state == 0:
			color = self.highlight_color
		self.render_play_pause(color, startx, starty)
		
		color = self.menu_color
		if menu == 0 and self.sub_menu_state == 1:
			color = self.highlight_color
		self.render_volume_up(color, startx + 20, starty)
		
		color = self.menu_color
		if menu == 0 and self.sub_menu_state == 2:
			color = self.highlight_color
		self.render_volume_down(color, startx + 40, starty)
		
		color = self.menu_color
		if menu == 0 and self.sub_menu_state == 3:
			color = self.highlight_color	
		self.render_seek_back(color, startx + 60, starty+2)
		
		color = self.menu_color
		if menu == 0 and self.sub_menu_state == 4:
			color = self.highlight_color
		self.render_seek_forward(color, startx + 80, starty+2)
		
		color = self.back_btn_color
		if menu == 0 and self.sub_menu_state == 5:
			color = self.back_highlight_color
		self.render_exit(color, startx + 100, starty+2)
		
		self.render_volume(starty)
		
	def render_play_pause(self, color, sx, sy):	
		if self.mpc.is_paused:
			pygame.draw.line(self.menu, color, [sx,sy+1],[sx,sy+10], 2)
			pygame.draw.line(self.menu,  color, [sx+5,sy+1],[sx+5,sy+10], 2)
		else:
			pygame.draw.lines(self.menu, color, 1, ([sx,sy+2],[sx+8,sy+6],[sx,sy+10]), 2)
			
	def render_volume_up(self, color, sx, sy):
		pygame.draw.line(self.menu, color, [sx,sy+5],[sx+9,sy+5], 2)
		pygame.draw.line(self.menu,  color, [sx+4,sy+1],[sx+4,sy+10], 2)
		
	def render_volume_down(self, color, sx, sy):	
		pygame.draw.line(self.menu, color, [sx,sy+5],[sx+10,sy+5], 2)
		
	def render_seek_back(self, color, sx, sy):
		pygame.draw.lines(self.menu, color, 0, ([sx+5,sy],[sx,sy+3],[sx+5,sy+6]), 2)
		
	def render_seek_forward(self, color, sx, sy):
		pygame.draw.lines(self.menu, color, 0, ([sx,sy],[sx+5,sy+3],[sx,sy+6]), 2)
	
	def render_exit(self, color, sx, sy):
		#pygame.draw.rect(self.menu, self.menu_bg_color, (sx,sy,10,10))
		pygame.draw.line(self.menu, color, [sx,sy],[sx+6,sy+6], 2)
		pygame.draw.line(self.menu,  color, [sx+6,sy],[sx,sy+6], 2)
	
	def render_volume(self, sy):
		volume = self.mpc.get_volume()
		surface = self.menu_font.render(volume, 1, self.back_btn_color)
		self.menu.blit( surface, (160 - surface.get_width() - 3, sy) )
	
	def render_sub_controls(self):
		sy = 84
		self.menu.fill((0,0,0),(0, sy, self.menu_width, self.menu_height - sy))
		self.render_back_button(sy)
	
	#
	# render_back_button
	#
	def render_back_button(self, sy):
		if self.back_button == True:
			sur = self.menu_font.render('BACK', 1, self.back_highlight_color, (0,0,0))
		else:
			sur = self.menu_font.render('BACK', 1, self.back_btn_color, (0,0,0))
		self.menu.blit( sur, (120, sy) )
	
	def on_screensaver_fire(self):
		self.screensaver_on = True
			
	#
	# update_surface
	# blit FMU Scroll
	# blit menu if menu_updated flag is True
	#
	def update_surface(self):
		self.surface.fill(self.fmu_scroll.bg_color, self.fmu_scroll.display_rect)
		self.surface.blit(self.fmu_scroll.surface, [self.fmu_scroll.xpos, 0])
		if self.screensaver_on == False:
			if self.menu_updated == True:
				self.surface.blit(self.menu, (0, 30))
				self.menu_updated = False
		else:
			self.surface.blit(self.screensaver.update_surface(), (0,30))
		return self.surface
	
	def toggleBackButton(self):
		self.back_button = not self.back_button
		self.update_menu()
		
	def do_back_button(self):
		self.back_button = False
		self.set_states(0,0,0)
	
	def get_archives(self):
		full = feedparser.parse('http://www.wfmu.org/archivefeed/mp3.xml')
		for entry in full.entries:
			archive = dict()
			archive['title'] = self.filter_stream_name(entry.title)
			archive['url'] = entry.link
			FMUApp.archives.append(archive)
		self.got_archives = True
				
	def filter_stream_name(self,raw):
		rdict = {
			'WFMU Freeform Radio' : 'WFMU',
			'with ' : 'w/',
			'Give the Drummer Some' : 'GtDS',
			'Give the Drummer Radio on WFMU' : 'GtDR',
			'Rock \'n\' Soul Ichiban from WFMU' : 'Ichiban',
			'UbuWeb Radio on WFMU' :  'Ubu',
			'Radio Boredcast on WFMU' : 'Boredcast',
			'WFMU MP3 Archive: ' : ''
		}
		robj = re.compile('|'.join(rdict.keys()))
		return robj.sub(lambda m: rdict[m.group(0)], raw)

#
# FMUScroll Class
# maintains the scrolling text (surface) that displays mpc current
#
class FMUScroll:
	def __init__(self, xpos, color):
		self.xpos = self.startx = xpos
		self.font = pygame.font.Font('/home/pi/fonts/FrutiIta.ttf', 20) 
		self.text = ''
		self.text_color = color
		self.bg_color = (0,0,0);
		self.surface = self.font.render(self.text, 1, self.text_color)
		self.display_rect = (0,0,160,30)
		self.text_rect = self.surface.get_rect()
		
		self.start_scroll_thread()
		
	def start_scroll_thread(self):
		try:
			self.thread = thread.start_new_thread( self.scroll, ())
		except:
		   print "Error: FMUScroll unable to start thread"

	def update_surface(self, text):
		self.text = text
		self.surface = self.font.render(self.text, 1, self.text_color)
		self.text_rect = self.surface.get_rect()
		self.xpos = self.startx + 1
		return self.surface
	
	def scroll(self):
		while 1:
			self.xpos -= 1
			if self.xpos <= -self.text_rect.right:
				self.xpos = self.startx
			time.sleep(.008)

#
# FMUScreensaver Class
#
class FMUScreensaver:
	def __init__(self, size):
		self.size = size
		self.fire = EventHook()
		self.stop_flag = False
		self.increment = .5
		self.trigger = 10
		self.surface = pygame.Surface(self.size)
		self.img = pygame.image.load('raspberrypi_logo.gif')
		self.bounds = self.img.get_rect()
	
	def start(self):
		self.vx = random.random() * 2 - 1
		self.vy = random.random() * 2 - 1
		self.imgx = 0
		self.imgy = 0
		self.cnt = 0
		self.stop_flag = False
		self.start_timer()
	
	def stop(self):
		self.stopFlag = True
			
	def update_surface(self):
		self.surface.fill((0,0,0))
		self.imgx = self.imgx + self.vx
		self.imgy = self.imgy + self.vy
		self.check_bounds()
		self.surface.blit(self.img, [self.imgx, self.imgy])
		return self.surface
		
	def check_bounds(self):
		if self.imgx + self.bounds.width > self.size[0]:
			self.vx = self.vx * -1
			self.imgx = self.size[0] - self.bounds.width
		elif self.imgx < 0:
			self.vx = self.vx * -1
			self.imgx = 0
		if self.imgy + self.bounds.height > self.size[1]:
			self.vy = self.vy * -1
			self.imgy = self.size[1] - self.bounds.height
		elif self.imgy < 0:
			self.vy = self.vy * -1
			self.imgy = 0
		
	def start_timer(self):
		try:
			self.timer = thread.start_new_thread( self.wait, ())
		except:
		   print "Error: FMUScreensaver unable to start thread"
	
	def wait(self):
		while self.stop_flag == False:
			self.cnt = self.cnt + self.increment
			if(self.cnt >= self.trigger):
				self.cnt = 0
				self.fire.fire()
				self.reset()
				#return
			else:
				time.sleep(self.increment)
		
	def reset(self):
		self.cnt = 0

#
# BTNS Class
# maintains a thread checking GPIO buttons
#                     
class BTNS:
	def __init__(self):
		self.change = EventHook()
		self.buttons = [
			{'pin':4, 'dir':'left'},
			{'pin':22, 'dir':'right'},
			{'pin':17, 'dir':'up'},
			{'pin':21, 'dir':'down'},
			{'pin':23, 'dir':'center'}
		]
		for btn in self.buttons:
			GPIO.setup( btn['pin'], GPIO.IN, pull_up_down=GPIO.PUD_UP)
		
		self.startListener()
			
	def startListener(self):
		try:
			thread.start_new_thread( self.check_buttons, ())
		except:
		   print "Error: BTNS unable to start thread"

	def check_buttons(self):
		while 1:
			for btn in self.buttons:
				if GPIO.input(btn['pin']):
					self.change.fire(btn['dir'])
					time.sleep(.2)
					break
					
#
# MPC class
# maintains a thread listening for mpc changes
#
class MPC:
	def __init__(self):
		self.is_paused = False
		self.volume = self.run_cmd('mpc volume')[7:10].strip()
		self.change = EventHook()

	def start(self):
		self.stop_flag = False
		self.startListener()
	
	def stop(self):
		self.stop_flag = True
				
	def run_cmd(self,cmd):
		p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
		output = p.communicate()[0]
		return output
	
	def seek(self,forward):
		if forward:
			self.run_cmd('mpc seek +5%')
		else:
			self.run_cmd('mpc seek -5%')
			
	def set_volume(self,up):
		if up:
			self.run_cmd( 'mpc volume +2' )	
		else:
			self.run_cmd( 'mpc volume -2' )
	
	def get_volume(self):
		return self.volume
		
	def toggle_pause(self):
		if self.is_paused == 1:
			self.run_cmd('mpc play')
		else:
			self.run_cmd('mpc pause')
	
	def load_stream(self, url):
		self.run_cmd('mpc clear')
		self.run_cmd('mpc add ' + url)
		self.run_cmd('mpc play')
		self.run_cmd('mpc current')
	
	def play_track(self,url):
		self.run_cmd('mpc clear')
		self.run_cmd('mpc add ' + url)
		self.run_cmd('mpc play')
	
	def startListener(self):
		try:
			self.thread = thread.start_new_thread( self.get_stats, ())
			return thread
		except:
		   print "Error: MPC unable to startListener"
		   
	def get_stats(self):
		while 1:
			change = self.run_cmd('mpc idle player mixer')	
			if change.strip() == 'player':
				current = self.run_cmd( 'mpc current')
				status = self.run_cmd('mpc status')
				lines = status.splitlines()
				pause_change = False
				if len(lines) > 1:
					line_two_status = lines[1][lines[1].find('[')+1:lines[1].find(']')]
					if line_two_status == 'paused' and self.is_paused == False:
						self.is_paused = True
						pause_change = True
					elif line_two_status == 'playing' and self.is_paused == True:
						self.is_paused = False
						pause_change = True
				self.change.fire({'type' : 'player', 'data': [current,status,pause_change]})
			elif change.strip() == 'mixer':
				self.volume = self.run_cmd('mpc volume')[7:10].strip()
				self.change.fire({'type':'mixer', 'data': [self.volume]})

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
		self.highlight_color = (249,240,97)
		self.menu_bg_color = (60,44,28)
		
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
		
		self.fmu = FMUApp(self.screen_size)
		#self.camera = CameraApp(self.screen_size)
		self.menu_array = [
			{'title':'FMU', 'app':self.fmu}
			#{'title':'camera', 'app':self.camera}
		]
		
		self.current_app = self.fmu
		
		self.btns = BTNS()
		self.btns.change += self.on_button_change
		
		self.screensaver = FMUScreensaver(self.screen_size)
		self.screensaver_on = False
		self.screensaver.fire += self.on_screensaver_fire
		
		self.update_menu()
		
	def on_screensaver_fire(self):
		pass
		#self.screensaver_on = True
		
	def on_button_change(self, dir):
		if self.app_state == 0:
			
			if self.screensaver_on == True:
				self.screensaver_on = False
			self.screensaver.reset()
			
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
	
	def on_app_exit(self):
		self.current_app.exit -= self.on_app_exit
		self.set_states(0,self.menu_state)
		
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
		if self.app_state == 0:
			if self.screensaver_on == False:
				if self.menu_updated == True:
					self.background.blit(self.menu, (0,0))
					self.menu_updated = False
			else:
				self.screensaver.update_surface()
				self.background.blit(self.screensaver.surface, (0,0))
		
		else:
			current_app = self.menu_array[self.menu_state]
			self.background.blit(self.current_app.update_surface(), [0,0])
		
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