# A new evolution simulator, as the old one was poorly coded and difficult to maintain, as well as hopelessly full of unfixable bugs
# Bert Myroon
# 13 Sept, 2018

import pygame
from pygame.locals import *

from random import randint
from random import random
from random import seed

from math import radians, ceil, floor

from time import time

from lib import Organism
from lib import UI
from lib import Button
from lib import Globals
from lib import Environment
from lib import Text
from lib import Constants
from lib import Quadtree

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

		self.nutrientmap = []
		self.moisturemap = []
		self.heatmap = []
		self.regenmap = [] # Values on the regenmap correspond to tile regeneration rates on the nutrient map

		self.map_surface = pygame.Surface((screen_dimensions_without_hud[0], screen_dimensions_without_hud[1]))
		self.camera_offset = [0, 0]

		self.target_organism = None

		self.total_creature_count = 0

		self.toggle = False

	def generate_random_organism(self, x=False, y=False):
		self.total_creature_count += 1
		if not x:
			x = randint(0, Constants.MAP_WIDTH*Constants.ENVIRONMENT_ZONE_SIZE)
		if not y:
			y = randint(0, Constants.MAP_HEIGHT*Constants.ENVIRONMENT_ZONE_SIZE)
		pc = randint(3, 10)
		return Organism.Organism(
			[x, # Random x position for organism
			y], # Random y position for organism
			{
			"colour": (
				randint(0, 255), # Random red value
				randint(0, 255), # Random green value
				randint(0, 255)  # Random blue value
				),
			"point_count": pc,
			"arm_chances_per_point": [random() for i in range(pc)],
			"arm_strength_per_arm": [random()for i in range(pc)],
			"size": randint(10, 32),
			"behaviour_bias": random()*2-1,
			"temp_regulator": random()*4-2,
			"input_weights": [random()*2-1 for i in range(Constants.INPUT_NODES)],
			"hidden_weights": [random()*2-1 for i in range(Constants.HIDDEN_NODES)],
			"output_weights": [random()*2-1 for i in range(Constants.OUTPUT_NODES)]
			}, 1, self.total_creature_count
			)

	def draw_maps(self):
		# Render nutrientmap currently in view
		self.map_surface.fill(UI.BACKGROUND_COLOUR)
		for x in range(self.camera_offset[0], round(screen_dimensions_without_hud[0]/Constants.ENVIRONMENT_ZONE_SIZE) + self.camera_offset[0]):
			for y in range(self.camera_offset[1], round(screen_dimensions_without_hud[1]/Constants.ENVIRONMENT_ZONE_SIZE) + self.camera_offset[1]):
				pygame.draw.rect(self.map_surface, Environment.get_colour(self.nutrientmap[x][y], self.heatmap[x][y], self.moisturemap[x][y]),
					((x-self.camera_offset[0])*Constants.ENVIRONMENT_ZONE_SIZE, (y-self.camera_offset[1])*Constants.ENVIRONMENT_ZONE_SIZE,
						Constants.ENVIRONMENT_ZONE_SIZE, Constants.ENVIRONMENT_ZONE_SIZE))
				if self.toggle:
					Text.draw_text((x-self.camera_offset[0])*Constants.ENVIRONMENT_ZONE_SIZE, (y-self.camera_offset[1])*Constants.ENVIRONMENT_ZONE_SIZE,
						str(round(self.heatmap[x][y])), UI.TEXT_SIZE, (255, 90, 0), self.map_surface)

	def position_to_screen_position(self, pos):
		if len(pos) > 2: # Return a rect if a rect is passed
			return [pos[0]-self.camera_offset[0]*Constants.ENVIRONMENT_ZONE_SIZE, pos[1]-self.camera_offset[1]*Constants.ENVIRONMENT_ZONE_SIZE, pos[2], pos[3]]

		return [pos[0]-self.camera_offset[0]*Constants.ENVIRONMENT_ZONE_SIZE, pos[1]-self.camera_offset[1]*Constants.ENVIRONMENT_ZONE_SIZE]

	def position_to_map_position(self, pos, screenpos=False):
		pos2 = pos
		if not screenpos:
			pos2 = self.position_to_screen_position(pos2)
		new_x = floor(pos2[0]/Constants.ENVIRONMENT_ZONE_SIZE)+self.camera_offset[0]
		new_y = floor(pos2[1]/Constants.ENVIRONMENT_ZONE_SIZE)+self.camera_offset[1]
		if new_x < 0:
			new_x = 0
		elif new_x >= Constants.MAP_WIDTH:
			new_x = Constants.MAP_WIDTH - 1
		if new_y < 0:
			new_y = 0
		elif new_y >= Constants.MAP_HEIGHT:
			new_y = Constants.MAP_HEIGHT - 1
		
		return [new_x, new_y]

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

										print("Generating environment...")
										gen_hmap_start_time = time()
										
										self.nutrientmap = Environment.generate_noisemap(Constants.MAP_WIDTH, Constants.MAP_HEIGHT)
										self.heatmap = Environment.generate_noisemap(Constants.MAP_WIDTH, Constants.MAP_HEIGHT, Constants.HEATMAP_MULTIPLER) # Less intense heatmap
										self.moisturemap = Environment.generate_noisemap(Constants.MAP_WIDTH, Constants.MAP_HEIGHT)
										self.regenmap = Environment.generate_noisemap(Constants.MAP_WIDTH, Constants.MAP_HEIGHT, 1/Constants.REPLENISH_DIVISOR)
										
										gen_hmap_end_time = time()
										print("Done. Took "+str(gen_hmap_end_time - gen_hmap_start_time)+" seconds.")
										del gen_hmap_start_time, gen_hmap_end_time
										
										print("Rendering environment...")
										
										rend_hmap_start_time = time()
										self.draw_maps()
										
										rend_hmap_end_time = time()
										print("Done. Took "+str(rend_hmap_end_time - rend_hmap_start_time)+" seconds.")
										del rend_hmap_start_time, rend_hmap_end_time
										

										for i in range(Constants.STARTING_POPULATION):
											self.organisms.append(self.generate_random_organism())
											self.organisms[-1].limit_position()

										mainscreen_timestamp = time()
										respawn_timestamp = time()

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
							pass

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

						if main_event.key == K_k:
							self.toggle *= -1
							self.toggle += 1

						if main_event.key == K_w:
							if self.camera_offset[1] > 0:
								self.camera_offset[1] -= 1
								self.draw_maps()

						if main_event.key == K_a:
							if self.camera_offset[0] > 0:
								self.camera_offset[0] -= 1
								self.draw_maps()

						if main_event.key == K_s:
							if self.camera_offset[1] < Constants.MAP_HEIGHT-round(screen_dimensions_without_hud[1]/Constants.ENVIRONMENT_ZONE_SIZE):
								self.camera_offset[1] += 1
								self.draw_maps()

						if main_event.key == K_d:
							if self.camera_offset[0] < Constants.MAP_WIDTH-round(screen_dimensions_without_hud[0]/Constants.ENVIRONMENT_ZONE_SIZE):
								self.camera_offset[0] += 1
								self.draw_maps()

					if main_event.type == pygame.KEYUP:
						if main_event.key == K_x:
							pass
					if main_event.type == pygame.MOUSEBUTTONDOWN:
						if main_event.button == 1:
							'''mousepom = self.position_to_map_position(pygame.mouse.get_pos(), True)
							print("mouse pom", mousepom)
							self.heatmap[mousepom[0]][mousepom[1]] = 1000000'''

							for organism in self.organisms:
								if pygame.Rect.colliderect(pygame.Rect(self.position_to_screen_position(organism.get_hitbox())),
									(pygame.mouse.get_pos()[0],pygame.mouse.get_pos()[1],1,1)):
									self.target_organism = organism

							for button in self.buttons:
								if button.hovered:
									button.activate()

				# Mainscreen logic below
				screen.fill(UI.BACKGROUND_COLOUR)
				screen.blit(self.map_surface, (0, 0))

				current_time = time()

				if len(self.organisms) < Constants.POPULATION_MINIMUM and current_time - respawn_timestamp >= Constants.RESPAWN_DELAY:
					for i in range(Constants.POPULATION_MINIMUM - len(self.organisms)):
						self.organisms.append(self.generate_random_organism())
						self.organisms[-1].limit_position()
						respawn_timestamp = time()
				
				if current_time - mainscreen_timestamp >= Constants.MAP_REFRESH_DELAY:
					# Delete the dead organisms and re-render the map every few seconds
					# Also give energy to the map so the organisms have an energy source
					for organism in self.organisms[:]:
						if organism.get_dead():
							self.organisms.remove(organism)
					mainscreen_timestamp = time()
				
					for x in range(Constants.MAP_WIDTH):
						for y in range(Constants.MAP_HEIGHT):
							if self.nutrientmap[x][y] < Constants.ENVIRONMENT_SCALING:
								self.nutrientmap[x][y] += self.regenmap[x][y]

					self.draw_maps()
				
				for button in self.buttons:
					button.update()
					button.draw()

				qt_width = Constants.MAP_WIDTH*Constants.ENVIRONMENT_ZONE_SIZE
				qt_height = Constants.MAP_HEIGHT*Constants.ENVIRONMENT_ZONE_SIZE
				self.quadtree = Quadtree.Quadtree(Quadtree.CentreRect(qt_width/2, qt_height/2, qt_width, qt_height), Constants.QUADTREE_CAPACITY)
				del qt_width, qt_height

				for organism in self.organisms:
					pom = self.position_to_map_position(organism.get_hitbox())
					if not organism.get_dead():
						organism.update(self.heatmap[pom[0]][pom[1]], self.moisturemap[pom[0]][pom[1]])
						
						# Make the organism eat if in a neutral mood
						if organism.get_mood_name() == "Neutral":
							if self.nutrientmap[pom[0]][pom[1]] > 0:
								organism.shift_energy(organism.get_size()*Constants.EAT_GAIN_MULTIPLIER)
								self.nutrientmap[pom[0]][pom[1]] -= organism.get_size()#*Constants.EAT_GAIN_MULTIPLIER

						organism_map_position = self.position_to_map_position(organism.get_position())

						organism.make_decision([],
							[self.nutrientmap[organism_map_position[0]][organism_map_position[1]],
							self.heatmap[organism_map_position[0]][organism_map_position[1]],
							self.moisturemap[organism_map_position[0]][organism_map_position[1]]])
						
						organism.draw(screen, [o*Constants.ENVIRONMENT_ZONE_SIZE for o in self.camera_offset])
						self.quadtree.insert((organism.get_position()[0], organism.get_position()[1], organism))

				if self.toggle:
					self.quadtree.draw(screen, [o*Constants.ENVIRONMENT_ZONE_SIZE for o in self.camera_offset])

				for organism in self.organisms:
					vision_collide_points = self.quadtree.query(Quadtree.NormalRect(organism.get_vision_hitbox_points()))
					organism_collide_points = self.quadtree.query(Quadtree.NormalRect(organism.get_hitbox_points()))
					colliding_organisms = [o[2] for o in organism_collide_points]
					seen_organisms = [o[2] for o in vision_collide_points]

					for other_organism in colliding_organisms:
						organism.bump(other_organism.get_velocity()[0])
						if organism != other_organism:
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

							elif organism.get_mating():# and other_organism.get_mating():
								# Reproduce
								if len(self.organisms) < Constants.POPULATION_LIMIT:
									organism.shift_energy(-organism.get_size()*Constants.REPRODUCTION_COST_MULTIPLIER)
									other_organism.shift_energy(-other_organism.get_size()*Constants.REPRODUCTION_COST_MULTIPLIER)
									average_energy_loss = ((organism.get_size()*Constants.REPRODUCTION_COST_MULTIPLIER)+(other_organism.get_size()*Constants.REPRODUCTION_COST_MULTIPLIER))//2

									average_position = [(p1+p2)/2 for p1, p2 in zip(organism.get_position(), other_organism.get_position())]

									pc = (organism.get_point_count() + other_organism.get_point_count())//2 + round(random()-0.3)*randint(-1, 1)
									minpc = min(organism.get_point_count(), other_organism.get_point_count())
									if pc > minpc:
										# Need extra arm stats
										ac = [(organism.get_arm_chances()[i] + other_organism.get_arm_chances()[i])/2 for i in range(minpc)]
										ac += [random() for i in range(pc - minpc)]
										
									else:
										# We're good
										ac = [(organism.get_arm_chances()[i] + other_organism.get_arm_chances()[i])/2 for i in range(pc)]

									minaco = min(len(organism.get_arms()), len(other_organism.get_arms()))									
									astr = [(organism.get_arm_strengths()[i] + other_organism.get_arm_strengths()[i])/2 for i in range(minaco)]
									if pc > minaco:
										# Need extra arm strengths
										astr += [random() for i in range(pc - minaco)]

									'''print("repro point count: ", pc)
									print("repro chances: ", len(ac))
									print("repro strengths: ", len(astr))'''
									
									average_gene_dict = {"colour": tuple([(c1+c2)/2 for c1, c2 in zip(organism.get_colour(), other_organism.get_colour())]),
									"point_count": pc,
									"arm_chances_per_point": ac,
									"arm_strength_per_arm": astr,
									"size": (organism.get_size() + other_organism.get_size())//2 + round(random()-0.3)*randint(-1, 1),
									"behaviour_bias": (organism.get_behaviour_bias() + other_organism.get_behaviour_bias())/2 + (random()*2 - 1) / 8,
									"temp_regulator": (organism.get_temp_regulator() + other_organism.get_temp_regulator())/2 + (random()*2 - 1) / 8,
									"input_weights": [(iw1+iw2)/2 + (random()*2 - 1) / 8 for iw1, iw2 in zip(organism.get_input_weights(), other_organism.get_input_weights())],
									"hidden_weights": [(hw1+hw2)/2 + (random()*2 - 1) / 8 for hw1, hw2 in zip(organism.get_hidden_weights(), other_organism.get_hidden_weights())],
									"output_weights": [(ow1+ow2)/2 + (random()*2 - 1) / 8 for ow1, ow2 in zip(organism.get_input_weights(), other_organism.get_input_weights())]}
									# (random()*2 - 1) / 8 is a weight mutation. This value should be studied closely, as it is the "step size" for the neural net

									average_generation = max([organism.get_generation(), other_organism.get_generation()])+1

									average_id = min(organism.get_id(), other_organism.get_id()) # Someone's id has to win out. I'll use the lower one
									#print("repro id: ", average_id)

									# Pick a polygon at random for the child.
									average_polygon = [organism.get_original_polygon(), other_organism.get_original_polygon()][randint(0, 1)]

									# Finally, the offspring is created!
									self.organisms.append(Organism.Organism(average_position, average_gene_dict, average_generation, average_id, average_energy_loss, average_polygon))
									self.organisms[-1].limit_position() # Just in case
									
									organism.set_mating(False)
									other_organism.set_mating(False)

									organism.set_time_left_before_mating(organism.get_reproduction_wait_period())
									other_organism.set_time_left_before_mating(other_organism.get_reproduction_wait_period())

					for seen_organism in seen_organisms:
						if organism != seen_organism:
							
							organism_map_position = self.position_to_map_position(organism.get_position())
							organism.make_decision([seen_organism],
								[self.nutrientmap[organism_map_position[0]][organism_map_position[1]],
								self.heatmap[organism_map_position[0]][organism_map_position[1]],
								self.moisturemap[organism_map_position[0]][organism_map_position[1]]])

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
						"Time left: "+str(self.target_organism.get_time_left())+"/"+str(Constants.ORGANISM_LIFESPAN))

					# Draw the organism's brain
					
					# Draw the input layer
					for n in range(len(self.target_organism.get_inputs())):
						pygame.draw.circle(screen, UI.NODE_DRAW_COLOUR, (screen_dimensions_without_hud[0]+UI.PADDING, 2*n*UI.NODE_DRAW_SIZE+186), UI.NODE_DRAW_SIZE)
						Text.draw_text(screen_dimensions_without_hud[0]+6, 2*n*UI.NODE_DRAW_SIZE+186-5,
						 str(round(self.target_organism.get_inputs()[n], 2)), UI.NODE_TEXT_SIZE, (255, 255, 255))
						Text.draw_text(screen_dimensions_without_hud[0]+20, 2*n*UI.NODE_DRAW_SIZE+186-5,
						 self.target_organism.get_input_names()[n], UI.NODE_TEXT_SIZE, (0, 0, 0))

					# Draw the hidden layer
					for n in range(len(self.target_organism.get_hidden_layer())):
						pygame.draw.circle(screen, UI.NODE_DRAW_COLOUR, (screen_dimensions_without_hud[0]+UI.PADDING+50, 2*n*UI.NODE_DRAW_SIZE+186), UI.NODE_DRAW_SIZE)
						Text.draw_text(screen_dimensions_without_hud[0]+50+6, 2*n*UI.NODE_DRAW_SIZE+186-5,
							str(round(self.target_organism.get_hidden_layer()[n], 2)), UI.NODE_TEXT_SIZE, (255, 255, 255))

					# Draw the output layer
					for n in range(len(self.target_organism.get_outputs())):
						pygame.draw.circle(screen, UI.NODE_DRAW_COLOUR, (screen_dimensions_without_hud[0]+UI.PADDING+100, 2*n*UI.NODE_DRAW_SIZE+186), UI.NODE_DRAW_SIZE)
						Text.draw_text(screen_dimensions_without_hud[0]+100+6, 2*n*UI.NODE_DRAW_SIZE+186-5,
							str(round(self.target_organism.get_outputs()[n], 2)), UI.NODE_TEXT_SIZE, (255, 255, 255))

				else:
					Text.draw_text(screen_dimensions_without_hud[0]+1*UI.PADDING, 0+1*UI.PADDING, "Click an organism for more info...", UI.HEADER_TEXT_SIZE)

				Text.draw_text(screen_dimensions_without_hud[0]+UI.PADDING, screen_dimensions_without_hud[1]-8-2*UI.PADDING,
					"Population: "+str(len(self.organisms))+"/"+str(Constants.POPULATION_LIMIT), UI.HEADER_TEXT_SIZE)

				pygame.display.flip() #Updates display
				clock.tick(60)


		pygame.quit() #Quits if all loops are exited


calev2 = Game()

calev2.gameloop()
