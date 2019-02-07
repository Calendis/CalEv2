# A new evolution simulator, as the old one was poorly coded and difficult to maintain, as well as hopelessly full of unfixable bugs
# Bert Myroon
# 13 Sept, 2018

import pygame
from pygame.locals import *

from random import randint
from random import random

from math import radians, ceil

from time import time

from lib import Organism
from lib import UI
from lib import Button
from lib import Globals
from lib import Environment
from lib import Text
from lib import Name
from lib import Constants

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

		self.zone_size = 70 # I just chose a zone size that seemed fastest
		self.zone_rows = ceil(screen_dimensions_without_hud[1]/self.zone_size)
		self.zone_columns = ceil(screen_dimensions_without_hud[0]/self.zone_size)
		self.zones = []
		self.zone_lists = []
		for i in range(self.zone_columns):
			for j in range(self.zone_rows):
				self.zones.append((self.zone_size*i, self.zone_size*j, self.zone_size, self.zone_size))
				self.zone_lists.append([])

		self.total_creature_count = 0


	def generate_random_organism(self):
		self.total_creature_count += 1
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
			"size": randint(10, 32),
			"behaviour_bias": random()*2-1,
			"input_weights": [random()*2-1 for i in range(15)],
			"output_weights": [random()*2-1 for i in range(3)]
			}, 1, Name.generate_name(), self.total_creature_count
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

										for i in range(Constants.STARTING_POPULATION):
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
						for zone in self.zones:
							if pygame.Rect.colliderect(pygame.Rect(organism.get_hitbox()), pygame.Rect(zone)):
								self.zone_lists[self.zones.index(zone)].append(organism)

						organism.draw(screen)

				for zone_list in self.zone_lists:
					for organism in zone_list:
						number_of_interactions = 0
						for other_organism in zone_list:
							if organism != other_organism:
								if max([self.point_in_triangle(p, other_organism.get_vision()) for p in organism.get_polygon()]):
									organism.make_decision([other_organism])
									number_of_interactions += 1

								if pygame.Rect.colliderect(pygame.Rect(organism.get_hitbox()), pygame.Rect(other_organism.get_hitbox())):
									if organism.get_aggression() or other_organism.get_aggression():
										# Attack
										if organism.get_aggression() and other_organism.get_aggression():
											# Both organisms take damage and gain energy
											organism.shift_fitness(-other_organism.get_attack())
											other_organism.shift_fitness(-organism.get_attack())
											organism.shift_energy(organism.get_attack())
											other_organism.shift_energy(other_organism.get_attack())

										else:
											for o in [organism, other_organism]:
												if not o.get_aggression:
													# o takes damage, and the other gets energy
													o.fitness -= [organism, other_organism][[organism, other_organism].index(o) - 1].get_attack()
													[[organism, other_organism].index(o) - 1].shift_energy([[organism, other_organism].index(o) - 1].get_attack())

									elif organism.get_mating() and other_organism.get_mating():
										# Reproduce
										if len(self.organisms) < Constants.POPULATION_LIMIT:
											organism.shift_energy(-organism.get_size()*10)
											other_organism.shift_energy(-other_organism.get_size()*10)

											average_position = [(p1+p2)/2 for p1, p2 in zip(organism.get_position(), other_organism.get_position())] 

											average_gene_dict = {"colour": tuple([(c1+c2)/2 for c1, c2 in zip(organism.get_colour(), other_organism.get_colour())]),
											"point_count": (organism.get_point_count() + other_organism.get_point_count())//2 + round(random()*randint(-1, 1)+0.1),
											"size": (organism.get_size() + other_organism.get_size())//2 + round(random()*randint(-1, 1)+0.1),
											"behaviour_bias": (organism.get_behaviour_bias() + other_organism.get_behaviour_bias())/2 + (random() - (1/2))/4,
											"input_weights": [(iw1+iw2)/2 + (random() - (1/2))/4 for iw1, iw2 in zip(organism.get_input_weights(), other_organism.get_input_weights())],
											"output_weights": [(ow1+ow2)/2 + (random() - (1/2))/4 for ow1, ow2 in zip(organism.get_input_weights(), other_organism.get_input_weights())]}

											average_generation = max([organism.get_generation(), other_organism.get_generation()])+1

											average_name = organism.get_name() # There's no such thing as an "average name", so one organism just wins
											average_id = organism.get_id() # The same situation. Someone's id has to win out

											# Finally, the offspring is created!
											self.organisms.append(Organism.Organism(average_position, average_gene_dict, average_generation, average_name, average_id))

											organism.set_mating(False)
											other_organism.set_mating(False)

											organism.set_time_left_before_mating(organism.get_reproduction_wait_period())
											other_organism.set_time_left_before_mating(other_organism.get_reproduction_wait_period())

									number_of_interactions += 1

								if number_of_interactions >= Constants.ORGANISM_INTERACTION_LIMIT:
									break

				# UI drawing
				pygame.draw.rect(screen, (UI.UI_COLOUR), (screen_dimensions_without_hud[0], 0, screen_dimensions_without_hud[0], screen_dimensions[1]))

				if self.target_organism:
					Text.draw_text(screen_dimensions_without_hud[0]+1*UI.PADDING, 0+1*UI.PADDING, self.target_organism.get_name(), UI.HEADER_TEXT_SIZE)
					
					Text.draw_text(screen_dimensions_without_hud[0]+1*UI.PADDING, 8+2*UI.PADDING,
						"Generation: "+str(self.target_organism.get_generation()))

					Text.draw_text(screen_dimensions_without_hud[0]+1*UI.PADDING, 8+3*UI.PADDING,
						"Origin ID: "+self.target_organism.get_id(),
						UI.TEXT_SIZE)
					
					Text.draw_text(screen_dimensions_without_hud[0]+1*UI.PADDING, 8+4*UI.PADDING,
						"Fitness: "+str(self.target_organism.get_current_fitness())+"/"+str(self.target_organism.get_max_fitness()),
						UI.TEXT_SIZE)
					
					Text.draw_text(screen_dimensions_without_hud[0]+1*UI.PADDING, 8+5*UI.PADDING,
						"Energy: "+str(self.target_organism.get_current_energy())+"/"+str(self.target_organism.get_max_energy()),
						UI.TEXT_SIZE)

					if self.target_organism.get_object_detected():
						self.can_see_text = "Can see: "+self.target_organism.get_object_detected().get_name()
					else:
						self.can_see_text = "Can see: none"
					Text.draw_text(screen_dimensions_without_hud[0]+1*UI.PADDING, 8+6*UI.PADDING,
						self.can_see_text, UI.TEXT_SIZE)

					Text.draw_text(screen_dimensions_without_hud[0]+UI.PADDING, 8+7*UI.PADDING,
						"Nodes: "+str(self.target_organism.get_point_count()))

					Text.draw_text(screen_dimensions_without_hud[0]+UI.PADDING, 8+8*UI.PADDING,
						"Mood: "+self.target_organism.get_mood_name())

					Text.draw_text(screen_dimensions_without_hud[0]+UI.PADDING, 8+9*UI.PADDING,
						"Bias: "+str(self.target_organism.get_behaviour_bias()))

					Text.draw_text(screen_dimensions_without_hud[0]+UI.PADDING, 8+10*UI.PADDING,
						"In-brain: "+str(self.target_organism.get_input_weights()))

					Text.draw_text(screen_dimensions_without_hud[0]+UI.PADDING, 8+11*UI.PADDING,
						"Out-brain: "+str(self.target_organism.get_output_weights()))
				else:
					Text.draw_text(screen_dimensions_without_hud[0]+1*UI.PADDING, 0+1*UI.PADDING, "Click an organism for more info...", UI.HEADER_TEXT_SIZE)

				Text.draw_text(screen_dimensions_without_hud[0]+UI.PADDING, screen_dimensions_without_hud[1]-8-2*UI.PADDING,
					"Population: "+str(len(self.organisms))+"/"+str(Constants.POPULATION_LIMIT), UI.HEADER_TEXT_SIZE)

				pygame.display.flip() #Updates display
				clock.tick(60)


		pygame.quit() #Quits if all loops are exited


calev2 = Game()

calev2.gameloop()