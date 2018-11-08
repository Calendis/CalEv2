# A new evolution simulator, as the old one was poorly coded and difficult to maintain, as well as hopelessly full of unfixable bugs
# Bert Myroon
# 13 Sept, 2018

import pygame
from pygame.locals import *

from random import randint
from random import random

from math import radians

from time import time

from lib import Organism
from lib import UI
from lib import Button
from lib import Globals
from lib import Environment
from lib import Text

pygame.init()

screen_dimensions = (1300,700)
screen_dimensions_without_hud = (930, 700)
screen = pygame.display.set_mode(screen_dimensions)

clock = pygame.time.Clock()

pygame.display.set_caption("CalEv2") 

class Game():
	"""This class contains the gameloop"""
	def __init__(self):
		super(Game, self).__init__()
		self.done = False

		self.buttons = []
		self.buttons.append(Button.NewButton(16, 16))
		
		self.organisms = []

		self.heightmap = []
		self.moisture_map = []
		self.temperature_map = []

		self.heightmap_surface = pygame.Surface((screen_dimensions_without_hud[0], screen_dimensions_without_hud[1]))

		self.target_organism = None

		self.zone_size = 133
		self.zone_rows = 6
		self.zone_columns = 7
		self.zones = []
		self.zone_lists = []
		for i in range(self.zone_columns):
			for j in range(self.zone_rows):
				self.zones.append((self.zone_size*i, self.zone_size*j, self.zone_size, self.zone_size))
				self.zone_lists.append([])


	def generate_random_organism(self):
		return Organism.Organism(
			[randint(0, screen_dimensions_without_hud[0]), # Random x position for organism
			randint(0, screen_dimensions_without_hud[1])], # Random y position for organism
			{
			"colour": (
				randint(0, 255), # Random red value
				randint(0, 255), # Random green value
				randint(0, 255)  # Random blue value
				),
			"point_count": randint(3, 10),
			"size": randint(32, 33),
			"behaviour_bias": random()*2-1,
			"input_weights": [random()*2-1 for i in range(15)],
			"output_weights": [random()*2-1 for i in range(3)]
			}
			)

	def triangle_area(self, triangle):
		x1 = triangle[0][0]
		y1 = triangle[0][1]
		x2 = triangle[1][0]
		y2 = triangle[1][1]
		x3 = triangle[2][0]
		y3 = triangle[2][1]

		return abs((x1*(y2-y3) + x2*(y3-y1)+ x3*(y1-y2))/2)

	def point_in_triangle(self, point, triangle):
		total_area = self.triangle_area(triangle)

		triangle_1 = (point, triangle[1], triangle[2])
		area_1 = self.triangle_area(triangle_1)

		triangle_2 = (triangle[0], point, triangle[2])
		area_2 = self.triangle_area(triangle_2)

		triangle_3 = (triangle[0], triangle[1], point)
		area_3 = self.triangle_area(triangle_3)

		return (total_area == area_1+area_2+area_3)


	def gameloop(self):
		while not self.done:
			while not self.done and Globals.titlescreen: #For Multiple gameloops subsets. For example, a title screen and a pause screen
				title_events = pygame.event.get()

				for title_event in title_events:
					#Event handling
					if title_event.type == pygame.QUIT:
						self.done = True
					if title_event.type == pygame.KEYDOWN:
						if title_event.key == K_x:
							pass
					if title_event.type == pygame.KEYUP:
						if title_event.key == K_x:
							pass
					if title_event.type == pygame.MOUSEBUTTONDOWN:
						if title_event.button == 1:
							for button in self.buttons:
								if button.hovered:
									button.activate()

									if button.__class__ == Button.NewButton:
										'''
										An important block of code! It is run ONCE when the "New Simulation" button is pressed.
										You will find environment generation, etc. here
										'''

										self.buttons.clear()

										print("Generating heightmap...")
										gen_hmap_start_time = time()
										self.heightmap = Environment.generate_noisemap(screen_dimensions_without_hud[0], screen_dimensions_without_hud[1])
										gen_hmap_end_time = time()
										print("Done. Took "+str(gen_hmap_end_time - gen_hmap_start_time)+" seconds.")
										del gen_hmap_start_time, gen_hmap_end_time
										
										print("Rendering heightmap...")
										rend_hmap_start_time = time()
										self.heightmap_surface.fill(UI.BACKGROUND_COLOUR)
										for x in range(screen_dimensions_without_hud[0]):
											for y in range(screen_dimensions_without_hud[1]):
												pygame.draw.line(self.heightmap_surface, (Environment.get_colour(self.heightmap[x][y])), (x, y), (x, y))
										rend_hmap_end_time = time()
										print("Done. Took "+str(rend_hmap_end_time - rend_hmap_start_time)+" seconds.")
										del rend_hmap_start_time, rend_hmap_end_time
										
										#self.moisture_map = pass
										#self.temperature_map = pass

										for i in range(100):
											self.organisms.append(self.generate_random_organism())

										mainscreen_timestamp = time()

				#Titlescreen logic below
				screen.fill(UI.BACKGROUND_COLOUR)
				
				for button in self.buttons:
					button.update()
					button.draw()

				pygame.display.flip() #Updates display
				clock.tick(60)

			while not self.done and not Globals.titlescreen and Globals.mainscreen:
				main_events = pygame.event.get()

				for main_event in main_events:
					#Event handling
					if main_event.type == pygame.QUIT:
						self.done = True
					if main_event.type == pygame.KEYDOWN:
						if main_event.key == K_x:
							self.organisms.append(self.generate_random_organism())

						if main_event.key == K_UP:
							# self.organisms[0].acceleration[0] = -1
							pass

						if main_event.key == K_DOWN:
							# self.organisms[0].acceleration[0] = 1
							pass

						if main_event.key == K_RIGHT:
							# self.organisms[0].rotational_acceleration = -1
							pass

						if main_event.key == K_LEFT:
							# self.organisms[0].rotational_acceleration = 1
							pass

					if main_event.type == pygame.KEYUP:
						if main_event.key == K_x:
							pass
					if main_event.type == pygame.MOUSEBUTTONDOWN:
						if main_event.button == 1:
							for organism in self.organisms:
								if pygame.Rect.colliderect(pygame.Rect(organism.get_hitbox()), (pygame.mouse.get_pos()[0],pygame.mouse.get_pos()[1],1,1)):
									self.target_organism = organism

							for button in self.buttons:
								if button.hovered:
									button.activate()

				#Mainscreen logic below
				screen.fill(UI.BACKGROUND_COLOUR)
				
				current_time = time()
				if current_time - mainscreen_timestamp >= 5:
					# Delete the dead organisms every five seconds
					for organism in self.organisms[:]:
						if organism.get_dead():
							self.organisms.remove(organism)
					mainscreen_timestamp = time()
				
				screen.blit(self.heightmap_surface, (0, 0))
				
				for button in self.buttons:
					button.update()
					button.draw()

				for zone_list in self.zone_lists:
					zone_list.clear()

				for organism in self.organisms:
					if not organism.get_dead():
						organism.update()
						# The nested list comprehension provides a list of all other organisms that the current organism can see/interact with
						#organism.make_decision([o for o in self.organisms if o != organism and max([self.point_in_triangle(p, o.get_vision()) for p in organism.get_polygon()])])
						for zone in self.zones:
							if pygame.Rect.colliderect(pygame.Rect(organism.get_hitbox()), pygame.Rect(zone)):
								self.zone_lists[self.zones.index(zone)].append(organism)

						organism.draw(screen)

				for zone_list in self.zone_lists:
					for organism in zone_list:
						organism.make_decision([o for o in zone_list if o != organism and max([self.point_in_triangle(p, o.get_vision()) for p in organism.get_polygon()])])

				# UI drawing
				pygame.draw.rect(screen, (UI.UI_COLOUR), (screen_dimensions_without_hud[0], 0, screen_dimensions_without_hud[0], screen_dimensions[1]))

				if self.target_organism:
					Text.draw_text(screen_dimensions_without_hud[0]+1*UI.PADDING, 0+1*UI.PADDING, self.target_organism.get_name(), UI.HEADER_TEXT_SIZE)
					
					Text.draw_text(screen_dimensions_without_hud[0]+1*UI.PADDING, 8+2*UI.PADDING,
						"Lifespan: "+str(self.target_organism.get_current_lifespan())+"/"+str(self.target_organism.get_max_lifespan()),
						UI.TEXT_SIZE)
					
					Text.draw_text(screen_dimensions_without_hud[0]+1*UI.PADDING, 8+3*UI.PADDING,
						"Fitness: "+str(self.target_organism.get_current_fitness())+"/"+str(self.target_organism.get_max_fitness()),
						UI.TEXT_SIZE)
					
					Text.draw_text(screen_dimensions_without_hud[0]+1*UI.PADDING, 8+4*UI.PADDING,
						"Energy: "+str(self.target_organism.get_current_energy())+"/"+str(self.target_organism.get_max_energy()),
						UI.TEXT_SIZE)

					if self.target_organism.object_detected:
						self.can_see_text = "Can see: "+self.target_organism.object_detected.get_name()
					else:
						self.can_see_text = "Can see: none"
					Text.draw_text(screen_dimensions_without_hud[0]+1*UI.PADDING, 8+5*UI.PADDING,
						self.can_see_text, UI.TEXT_SIZE)

					Text.draw_text(screen_dimensions_without_hud[0]+UI.PADDING, 8+6*UI.PADDING,
						"Nodes: "+str(self.target_organism.get_point_count()))

				pygame.display.flip() #Updates display
				clock.tick(60)


		pygame.quit() #Quits if all loops are exited


calev2 = Game()

calev2.gameloop()