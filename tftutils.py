#!/usr/bin/python
import pygame
import time
import thread
import random
import RPi.GPIO as GPIO

#
# TFTApp
#
class TFTApp():
	
	def __init__(self, size, m_col, h_col, mb_col):
		
		self.surface = pygame.Surface(size)
		
		self.menu_color = m_col
		self.highlight_color = h_col
		self.menu_bg_color = mb_col
		
		self.app_state = 0
		self.menu_state = 0
		
		self.size = size

		self.menu_font_size = 16
		self.menu_line_height = 17
		self.menu_font = pygame.font.Font('/home/pi/fonts/FUTURA_N.TTF', self.menu_font_size) 
		self.menu = pygame.Surface(self.size)
		self.menu_updated = True
		
		self.menu_array = [
			{'title':'foo'},
			{'title':'exit'}
		]
		
		self.exit = EventHook()
	
	def start_app(self):
		self.update_menu()
	
	def on_button_change(self, dir):
		
		app = self.app_state
		menu = self.menu_state
		
		if dir == 'up':
			self.set_states(app,menu - 1)
		elif dir == 'down':
			self.set_states(app,menu + 1)
		elif dir == 'center':
			self.do_menu_option()
	
	def do_menu_option(self):
		option = self.menu_array[self.menu_state]['title']
		if option == 'exit':
			self.exit_app()
		else:
			self.app_state = 0
		
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

		self.update_menu()
	
	def update_menu(self):
		self.menu.fill(self.menu_bg_color)
		self.render_menu()
		
	def render_menu(self):
		ypos = 0
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
		return self.surface
		
	def exit_app(self):
		self.app_state = 0
		self.menu_state = 0
		self.exit.fire()

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
# TFTScreensaver Class
#
class TFTScreensaver:
	def __init__(self, origin, size):
		self.origin = origin
		self.size = size
		self.fire = EventHook()
		self.stop_flag = False
		self.increment = .5
		self.trigger = 60
		self.surface = pygame.Surface(self.size)
		self.img = pygame.image.load('/home/pi/pydocs/pytft/raspberrypi_logo.gif')
		self.img_rect = self.img.get_rect()
		
	def start(self):
		self.vx = random.random() * 2 - 1
		self.vy = random.random() * 2 - 1
		self.imgx = 0
		self.imgy = 0
		self.cnt = 0
		self.running = False
		self.stop_flag = False
		self.start_timer()
	
	def update_size(self, origin, size):
		self.origin = origin
		self.size = size
		self.surface = pygame.Surface(self.size)
		
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
		if self.imgx + self.img_rect.width > self.size[0]:
			self.vx = self.vx * -1
			self.imgx = self.size[0] - self.img_rect.width
		elif self.imgx < 0:
			self.vx = self.vx * -1
			self.imgx = 0
		if self.imgy + self.img_rect.height > self.size[1]:
			self.vy = self.vy * -1
			self.imgy = self.size[1] - self.img_rect.height
		elif self.imgy < 0:
			self.vy = self.vy * -1
			self.imgy = 0
		
	def start_timer(self):
		try:
			if self.running == False:
				self.timer = thread.start_new_thread( self.wait, ())
				self.running = True
		except:
		   print "Error: TFTScreensaver unable to start thread"
	
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
		self.running = False
		
	def reset(self):
		self.cnt = 0

GESTURE_MOVE_MIN = 50  # Minimum movement in pixels to call it a move
GESTURE_CLICK_MAX = 15  # Maximum movement in pixels to call it a click
GESTURE_PRESS_MIN = 500  # Minimum time to call a click a long press
# Gesture enumeration
GESTURE_NONE = -1
GESTURE_CLICK = 0
GESTURE_SWIPE_LEFT = 1
GESTURE_SWIPE_RIGHT = 2
GESTURE_SWIPE_UP = 3
GESTURE_SWIPE_DOWN = 4
GESTURE_LONG_PRESS = 5
GESTURE_DRAG_VERTICAL = 6
GESTURE_DRAG_HORIZONTAL = 7

class GestureDetector(object):
	
	def __init__(self):
		self.gesture = GESTURE_NONE
		self.x_start = 0
		self.y_start = 0
		self.x_moved = 0
		self.y_moved = 0
		self.drag_length = 0
		self.press_duration = 0
		self.x_start, self.y_start = pygame.mouse.get_pos()

	def capture_gesture(self, event):
		if event.type != pygame.MOUSEBUTTONDOWN:
			return GESTURE_NONE

		gesture_ended = False

		mouse_down_time = pygame.time.get_ticks()  # Start timer to detect long mouse clicks
		self.x_start, self.y_start = pygame.mouse.get_pos()  # Get click position (= start position for swipe)
		pygame.mouse.get_rel()  # Start tracking mouse movement
		mouse_down_time = pygame.time.get_ticks()

		while not gesture_ended:
			for event in pygame.event.get():

				if event.type == pygame.MOUSEBUTTONUP:  # Gesture end
					self.press_duration = pygame.time.get_ticks() - mouse_down_time
					self.x_moved, self.y_moved = pygame.mouse.get_rel()  # Movements since start gesture
					self.gesture = self.__determine_gesture_type()  # Determines the kind of gesture used
					gesture_ended = True

		return self.gesture

	def __determine_gesture_type(self):
		x = self.x_moved
		y = self.y_moved
		if self.press_duration < GESTURE_PRESS_MIN:
			if abs(x) <= GESTURE_MOVE_MIN:
				if abs(y) <= GESTURE_MOVE_MIN:
					if abs(x) < GESTURE_CLICK_MAX and abs(y) < GESTURE_CLICK_MAX:
						return GESTURE_CLICK  # Tap (click)
					else:
						return -1  # No idea what the user did
				elif y > GESTURE_MOVE_MIN:  # Down swipe
					return GESTURE_SWIPE_DOWN
				elif y < -GESTURE_MOVE_MIN:  # Up swipe
					return GESTURE_SWIPE_UP
			elif abs(y) <= GESTURE_MOVE_MIN:
				if x > GESTURE_MOVE_MIN:  # Left swipe
					return GESTURE_SWIPE_LEFT
				elif x < -GESTURE_MOVE_MIN:  # Right swipe
					return GESTURE_SWIPE_RIGHT
		elif self.press_duration >= GESTURE_PRESS_MIN:
			if abs(x) <= GESTURE_MOVE_MIN:
				if abs(y) <= GESTURE_MOVE_MIN:
					if abs(x) < GESTURE_CLICK_MAX and abs(y) < GESTURE_CLICK_MAX:
						return GESTURE_LONG_PRESS  # Long press
					else:
						return -1  # No idea what the user did
				elif abs(y) > GESTURE_MOVE_MIN:
					return GESTURE_DRAG_VERTICAL  # Vertical drag
			elif abs(y) <= GESTURE_MOVE_MIN:
				if abs(x) > GESTURE_MOVE_MIN:
					return GESTURE_DRAG_HORIZONTAL  # Horizontal drag
		else:
			pass
			return GESTURE_NONE

#
# BTNS Class
# handles pygame mouse events
#                     
class BTNS:
	def __init__(self):
		self.gesture_detect = GestureDetector()
		
	def process_mouse_event(self, event):
		
		if event.type != pygame.MOUSEBUTTONDOWN and event.type != pygame.MOUSEBUTTONDOWN:
			return None
		
		gesture = self.gesture_detect.capture_gesture(event)
		
		x = self.gesture_detect.x_start
		y = self.gesture_detect.y_start

		if gesture == GESTURE_CLICK: 
			
			
		#if gesture == GESTURE_SWIPE_LEFT and self.current_index - 1 >= 0:
			
		#if gesture == GESTURE_SWIPE_RIGHT and self.current_index + 1 < len(self.screen_list):
		
		#if gesture == GESTURE_SWIPE_UP or gesture == GESTURE_SWIPE_DOWN:
			
		
#
# BTNS_GPIO Class
# maintains a thread checking GPIO buttons
#                     
class BTNS_GPIO:
	def __init__(self):
		
		GPIO.setmode(GPIO.BCM)
		
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