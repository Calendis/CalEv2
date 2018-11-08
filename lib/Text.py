#Useful stuff related to pygame text rendering
import pygame
from lib import UI

screen = pygame.display.set_mode()

pygame.font.init()
font_path = "resources/fonts/Oxygen-Regular.ttf"

#Helper function for rendering and blitting pygame text in one.
def draw_text(x, y, text, size=UI.TEXT_SIZE, colour=(0, 0, 0), surface=screen, antialiased=1):
	rendered_text = sized_font(size).render(text, antialiased, colour)
	surface.blit(rendered_text, (x, y))

def sized_font(x):
	return pygame.font.Font(font_path, x)

def get_text_width(text, size=UI.TEXT_SIZE):
	rendered_text = sized_font(size).render(text, 1, (0, 0, 0))
	return rendered_text.get_width()