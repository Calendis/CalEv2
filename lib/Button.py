#Code for buttons
#Created by Calendis
import pygame

screen = pygame.display.set_mode()

from lib import Text #Use my text library!
from lib import UI
from lib import Globals

#The activate function should be called from the event loop!

class Button(): #Base class for buttons
	"""docstring for Button"""
	def __init__(self, x, y, text, width=False, height=False, colour=UI.BUTTON_COLOUR):
		super(Button, self).__init__()
		self.x = x
		self.y = y
		self.width = width
		self.height = height
		self.colour = colour
		self.hovered = False
		self.text = text

		if not self.width:
			self.width = Text.get_text_width(self.text)+UI.BUTTON_X_PADDING

		if not self.height:
			self.height = UI.BUTTON_HEIGHT + UI.BUTTON_Y_PADDING

		self.rect = (self.x, self.y, self.width, self.height)

	def update(self):
		if pygame.Rect.colliderect(pygame.Rect(self.x, self.y, self.width, self.height), pygame.Rect(pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1], 1, 1)):
			if not self.hovered:
				self.colour = (self.colour[0]+UI.BUTTON_HOVER_GLOW, self.colour[1]+UI.BUTTON_HOVER_GLOW, self.colour[2]+UI.BUTTON_HOVER_GLOW)
			self.hovered = True
		else:
			if self.hovered:
				self.colour = (self.colour[0]-UI.BUTTON_HOVER_GLOW, self.colour[1]-UI.BUTTON_HOVER_GLOW, self.colour[2]-UI.BUTTON_HOVER_GLOW)
			self.hovered = False
		
		#self.rect = (self.x, self.y, self.width, self.height) #Uncomment this line if your buttons need to change position

	def draw(self):
		pygame.draw.rect(screen, self.colour, self.rect)

		Text.draw_text(self.x+UI.BUTTON_X_PADDING/2, self.y+UI.BUTTON_Y_PADDING, self.text)

	def activate(self):
		print("Button "+str(self)+" activated.")

	def get_text(self):
		return self.text

	def get_hovered(self):
		return self.hovered

	def get_width(self):
		return self.width

	def get_height(self):
		return self.height

class NewButton(Button):
	"""Button which, when clicked starts a new simulation."""
	def __init__(self, x, y):
		super(NewButton, self).__init__(x, y, UI.NEW_BUTTON_TEXT)

	def activate(self):
		Globals.titlescreen = False
		Globals.mainscreen = True