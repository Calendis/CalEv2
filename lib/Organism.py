# Code for organisms for calev2
import pygame

from copy import deepcopy

from math import floor
from math import sin
from math import cos
from math import radians
from math import sqrt
from math import tanh

from random import randint
from random import random

from lib import Name

class Organism():
	
	"""The class for organisms. As opposed to creating separate animal and plants,
	in this version I am only going to have one organism type. Some may evolve to
	be animalistic, and some may evolve to be plant-like. I am going to try and be
	as general as possible and avoid arbitrariness. Classification of kingdom and species
	can/will be done from an outside perspective as in real life, as opposed to being a
	deeper property of the organism.

	The keys needed in the gene dictionary are:

	colour, point_count, size, behaviour_bias, input_weights, output_weights

	"""
			
	
	def __init__(self, position, gene_dict, generation=1):
		super(Organism, self).__init__()
		self.name = Name.generate_name()

		''' The gene dictionary and the following block control traits of the organism. '''
		self.gene_dict = gene_dict
		self.gene_dict["inverse_colour"] = (255 - self.gene_dict["colour"][0], 255 - self.gene_dict["colour"][1], 255 - self.gene_dict["colour"][2])
		self.max_energy = gene_dict["size"]*125
		self.max_fitness = gene_dict["size"]*25*gene_dict["point_count"] # Give an incentive to evolve more points
		self.max_lifespan = 1000 + randint(-200, 200)
		self.generation = generation
		
		self.current_energy = self.max_energy
		self.current_fitness = self.max_fitness / 2
		self.current_lifespan = self.max_lifespan
		self.dead = False

		self.position = position
		self.angle = 0 # Rotation, in degrees
		self.polygon = self.generate_polygon()
		self.original_polygon = deepcopy(self.polygon)
		self.front_point = self.polygon[0]
		self.back_point = self.polygon[floor(len(self.polygon)/2)+1]
		self.hitbox = self.get_new_hitbox()
		self.vision = self.get_new_vision()
		self.original_vision = deepcopy(self.vision)

		self.velocity = [0, 0] # velocity[0] is magnitude, and velocity[1] is angle, in degrees
		self.acceleration = [0, 0] # [0] is change in magnitude, [1] is change in angle
		self.rotational_velocity = 0
		self.rotational_acceleration = 0
		self.mood = random()*2-1 # Mood is between -1 and 1. -1 is max friendly (reproduction mode) while +1 is max unfriendly (kill mode)

		self.max_velocity = self.gene_dict["point_count"] / self.gene_dict["size"]
		self.max_rotational_velocity = 10/self.gene_dict["point_count"]

		# These are just default values for the sensory_input
		# Energy, fitness, bias, accel, rotaccel, vel, rotvel, nc size, nc fitness, nc r, nc g, nc b, nc distance, nc species, nc no. of points
		self.sensory_input = [self.current_energy, self.current_fitness, self.gene_dict["behaviour_bias"], self.acceleration[0], self.rotational_acceleration, self.velocity[0], self.rotational_velocity,
		1, 1, 1, 1, 1, 1, 1, 1]

		self.object_detected = None

	def update(self):
		
		self.velocity[0] += self.acceleration[0]
		self.rotational_velocity += self.rotational_acceleration

		self.position[0] += self.velocity[0]*sin(radians(self.angle))
		self.position[1] += self.velocity[0]*cos(radians(self.angle))
		self.old_angle = self.angle
		self.angle += self.rotational_velocity

		# Rotate all polygon points around front point
		for p in self.original_polygon:
			old_x = p[0]
			old_y = p[1]

			p[0] = old_x*cos(radians(self.old_angle-self.angle))-old_y*sin(radians(self.old_angle-self.angle))
			p[1] = old_y*cos(radians(self.old_angle-self.angle))+old_x*sin(radians(self.old_angle-self.angle))

		# Redefine our polygon as our position plus our new rotation
		for i in range(len(self.polygon)):
			self.polygon[i][0] = self.position[0] + self.original_polygon[i][0]
			self.polygon[i][1] = self.position[1] + self.original_polygon[i][1]


		# Rotate all vision points around front point
		for p in self.original_vision:
			old_x = p[0]
			old_y = p[1]

			p[0] = old_x*cos(radians(self.old_angle-self.angle))-old_y*sin(radians(self.old_angle-self.angle))
			p[1] = old_y*cos(radians(self.old_angle-self.angle))+old_x*sin(radians(self.old_angle-self.angle))

		# Redefine our vision as our vision position plus our new vision rotation
		for i in range(len(self.vision)):
			self.vision[i][0] = self.position[0] + self.original_vision[i][0]
			self.vision[i][1] = self.position[1] + self.original_vision[i][1]
		
		self.hitbox = self.get_new_hitbox()

		# Limit some stuff
		self.acceleration[0] = 0
		self.rotational_acceleration = 0
		
		if abs(self.velocity[0]) > self.max_velocity:
			self.velocity[0] = self.max_velocity*self.max_velocity/self.velocity[0]
		
		if abs(self.rotational_velocity) > self.max_rotational_velocity:
			self.rotational_velocity = self.max_rotational_velocity**2/self.rotational_velocity
		
		# This block is for energy consumption
		self.current_lifespan -= 1
		if self.current_lifespan < 0:
			self.die()

		self.current_energy -= self.gene_dict["point_count"] # It should take more energy to maintain more points
		self.current_energy -= self.gene_dict["size"] # Being larger should cost more absolute energy
		self.current_energy -= abs(self.acceleration[0]) # Inertia
		self.current_energy -= abs(self.rotational_acceleration)
		self.current_energy += 5 # Energy will be gained at rest. This is like sleeping
								 # Hopefully organisms will evolve to "sleep" when energy is low by not moving
		
		if self.current_energy < 0:
			self.current_fitness += self.current_energy
			self.current_energy = 0
		
		if self.current_fitness < 0:
			self.die()

	def make_decision(self, objects_detected):
		# energy, fitness, bias, nc size, nc fitness, nc r, nc g, nc b, nc distance, nc species, nc no. of points

		'''
		Taking sensory input as input nodes and giving values to output nodes based on random weights that will evolve
		'''
		self.sensory_input[0] = self.current_energy/self.max_energy
		self.sensory_input[1] = self.get_fitness_ratio()
		self.sensory_input[2] = self.gene_dict["behaviour_bias"]
		self.sensory_input[3] = self.acceleration[0]
		self.sensory_input[4] = self.rotational_acceleration
		self.sensory_input[5] = self.velocity[0]
		self.sensory_input[6] = self.rotational_velocity

		if len(objects_detected) > 0:
			self.object_detected = objects_detected[0]
			self.sensory_input[7] = objects_detected[0].get_size()
			self.sensory_input[8] = objects_detected[0].get_fitness_ratio()
			self.sensory_input[9] = objects_detected[0].get_colour()[0]
			self.sensory_input[10] = objects_detected[0].get_colour()[1]
			self.sensory_input[11] = objects_detected[0].get_colour()[2]
			self.sensory_input[12] = sqrt((self.get_position()[0]-objects_detected[0].get_position()[0])**2 + (self.get_position()[1]-objects_detected[0].get_position()[1])**2)
			self.sensory_input[13] = 1
			self.sensory_input[14] = objects_detected[0].gene_dict["point_count"]

		self.output_1, self.output_2, self.output_3 = 0, 0, 0
		for i in range(len(self.sensory_input)):
			self.output_1 += self.sensory_input[i]*self.gene_dict["input_weights"][i]
			self.output_2 += self.sensory_input[i]*self.gene_dict["input_weights"][i]
			self.output_3 += self.sensory_input[i]*self.gene_dict["input_weights"][i]
		
		self.output_1, self.output_2, self.output_3 = tanh(self.output_1), tanh(self.output_2), tanh(self.output_3)
		self.output_1 *= self.gene_dict["output_weights"][0]
		self.output_2 *= self.gene_dict["output_weights"][1]
		self.output_3 *= self.gene_dict["output_weights"][2]

		self.acceleration[0] = self.output_1
		self.rotational_acceleration = self.output_2
		self.mood = self.output_3

	def draw(self, surface):
		pygame.draw.polygon(surface, (self.gene_dict["colour"]), self.polygon)
		pygame.draw.line(surface, (self.gene_dict["inverse_colour"]), (self.front_point), (self.back_point))

		# Draws the organism's hitbox for debug purposes
		# pygame.draw.rect(surface, (255, 0, 0), self.hitbox, 1)

		# And the vision triangle
		# pygame.draw.polygon(surface, (0, 255, 255), self.vision, 1)

	def generate_polygon(self):
		points = []

		for p in range(self.gene_dict["point_count"]):
			points.append([randint(0, self.gene_dict["size"]), randint(0, self.gene_dict["size"])])

		t_x = 0
		t_y = 0

		for p in points:
			t_x += p[0]
			t_y += p[1]

		t_x /= len(points)
		t_y /= len(points)

		return points

	def get_new_hitbox(self):
		return [
			min(p[0] for p in self.polygon),
			min(p[1] for p in self.polygon),
			max(p[0] for p in self.polygon)-min(p[0] for p in self.polygon),
			max(p[1] for p in self.polygon)-min(p[1] for p in self.polygon)]

	def get_new_vision(self):
		front_vision_point = list(self.front_point)
		v = [front_vision_point,
			[front_vision_point[0]-self.gene_dict["size"], front_vision_point[1]+2*self.gene_dict["size"]],
			[front_vision_point[0]+self.gene_dict["size"], front_vision_point[1]+2*self.gene_dict["size"]]]
		
		return v

	def die(self):
		self.gene_dict["colour"] = (150, 150, 150)
		self.dead = True

	def get_name(self):
		return self.name

	def get_dead(self):
		return self.dead

	def get_hitbox(self):
		return self.hitbox

	def get_current_lifespan(self):
		return self.current_lifespan

	def get_max_lifespan(self):
		return self.max_lifespan

	def get_current_fitness(self):
		return self.current_fitness

	def get_max_fitness(self):
		return self.max_fitness

	def get_current_energy(self):
		return self.current_energy

	def get_max_energy(self):
		return self.max_energy

	def get_generation(self):
		return self.generation

	def get_size(self):
		return self.gene_dict["size"]

	def get_fitness_ratio(self):
		return self.current_fitness / self.max_fitness

	def get_colour(self):
		return self.gene_dict["colour"]

	def get_position(self):
		return self.position

	def get_vision(self):
		return self.vision

	def get_polygon(self):
		return self.polygon

	def get_point_count(self):
		return self.gene_dict["point_count"]