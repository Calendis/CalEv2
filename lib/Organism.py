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

from lib import Constants

class Organism():
	
	"""The class for organisms. As opposed to creating separate animal and plants,
	in this version I am only going to have one organism type. Some may evolve to
	be animal-like, and some may evolve to be plant-like. I am going to try and be
	as general as possible and avoid arbitrariness. Classification of kingdom and species
	can/will be done from an outside perspective as in real life, as opposed to being a
	deeper property of the organism.

	The keys needed in the gene dictionary are:

	colour, point_count, size, behaviour_bias, temp_regulator, input_weights, hidden_weights, output_weights

	"""
			
	def __init__(self, position, gene_dict, generation, name, idname, starting_energy=False, initial_polygon=False):
		super(Organism, self).__init__()
		self.name = name
		self.idname = idname

		''' The gene dictionary and the following block control traits of the organism. '''
		self.gene_dict = gene_dict
		self.gene_dict["inverse_colour"] = (255 - self.gene_dict["colour"][0], 255 - self.gene_dict["colour"][1], 255 - self.gene_dict["colour"][2])
		self.gene_dict["point_count"] = max(self.gene_dict["point_count"], 3)
		self.gene_dict["size"] = max(10, self.gene_dict["size"])
		self.max_energy = gene_dict["size"]*250
		self.max_fitness = gene_dict["size"]*25*gene_dict["point_count"] # Give an incentive to evolve more points
		self.time_left = Constants.ORGANISM_LIFESPAN
		self.generation = generation
		
		if not starting_energy:
			self.current_energy = self.max_energy
		else:
			self.current_energy = starting_energy

		self.current_fitness = self.max_fitness / 2
		self.dead = False

		self.position = position
		self.angle = 0 # Rotation, in degrees
		self.polygon = self.generate_polygon(initial_polygon)
		self.original_polygon = deepcopy(self.polygon)
		self.thinness = self.generate_thinness()
		self.perimeter = self.generate_perimeter()
		self.front_point = self.polygon[0]
		self.back_point = self.polygon[floor(len(self.polygon)/2)+1]
		self.hitbox = self.get_new_hitbox()
		self.vision = self.get_new_vision()
		self.original_vision = deepcopy(self.vision)
		self.vision_hitbox = self.get_new_vision_hitbox()

		self.velocity = [0, 0] # velocity[0] is magnitude, and velocity[1] is angle, in degrees
		self.acceleration = [0, 0] # [0] is change in magnitude, [1] is change in angle
		self.rotational_velocity = 0
		self.rotational_acceleration = 0
		
		self.mood = 0 # Mood is between -1 and 1. -1 is max friendly (reproduction mode) while +1 is max unfriendly (kill mode)
		self.internal_temp = 0

		self.max_velocity = self.gene_dict["point_count"] / self.gene_dict["size"]
		self.max_rotational_velocity = 10/self.gene_dict["point_count"]

		# These are just default values for the sensory_input
		# Energy, fitness, bias, accel, rotaccel, vel, rotvel, internal_temp, nc size, nc fitness, nc r, nc g, nc b, nc distance, nc species, nc no. of points
		self.sensory_input = [self.current_energy, self.current_fitness, self.gene_dict["behaviour_bias"], self.acceleration[0], self.rotational_acceleration,
		self.velocity[0], self.rotational_velocity, self.internal_temp,
		1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1] # Initialise some values to 1

		self.input_names = ["Energy", "Fit", "Bias", "Accel", "RotAccel", "Vel", "RotVel", "Temp",
		"NC Size", "NC Fit", "NC R", "NC G", "NC B", "NC Dist", "NC Spec", "NC Nodes", "Tl Nutr", "Tl Temp", "Tl Wet"]

		self.hidden_layer = [None]*Constants.HIDDEN_NODES

		self.object_detected = None

		self.aggression = False
		self.mating = False
		self.reproduction_wait_period = Constants.REPRODUCTION_WAIT_PERIOD
		self.time_left_before_mating = self.reproduction_wait_period

	def update(self, current_heat, current_moisture):
		self.velocity[0] += self.acceleration[0]
		self.rotational_velocity += self.rotational_acceleration

		self.position[0] += self.velocity[0]*sin(radians(self.angle))
		self.position[1] += self.velocity[0]*cos(radians(self.angle))
		self.old_angle = self.angle
		self.angle += self.rotational_velocity

		self.internal_temp += current_heat/Constants.ENVIRONMENT_SCALING*self.perimeter
		self.internal_temp -= self.gene_dict["temp_regulator"]
		if self.internal_temp < 0:
			self.internal_temp = 0

		# Rotate all polygon points around centre point
		for p in self.original_polygon:
			
			cx = self.get_centre_point()[0] - self.position[0]
			cy = self.get_centre_point()[1] - self.position[1]

			old_x = p[0] - cx
			old_y = p[1] - cy

			p[0] = old_x*cos(radians(self.old_angle-self.angle))-old_y*sin(radians(self.old_angle-self.angle))
			p[1] = old_y*cos(radians(self.old_angle-self.angle))+old_x*sin(radians(self.old_angle-self.angle))

			p[0] += cx
			p[1] += cy

		# Redefine our polygon as our position plus our new rotation
		for i in range(len(self.polygon)):
			self.polygon[i][0] = self.position[0] + self.original_polygon[i][0]
			self.polygon[i][1] = self.position[1] + self.original_polygon[i][1]

		# Rotate all vision points around centre point
		for p in self.original_vision:
			
			cx = self.get_centre_point()[0] - self.position[0]
			cy = self.get_centre_point()[1] - self.position[1]

			old_x = p[0] - cx
			old_y = p[1] - cy

			p[0] = old_x*cos(radians(self.old_angle-self.angle))-old_y*sin(radians(self.old_angle-self.angle))
			p[1] = old_y*cos(radians(self.old_angle-self.angle))+old_x*sin(radians(self.old_angle-self.angle))

			p[0] += cx
			p[1] += cy

		# Redefine our vision as our vision position plus our new vision rotation
		for i in range(len(self.vision)):
			self.vision[i][0] = self.position[0] + self.original_vision[i][0]
			self.vision[i][1] = self.position[1] + self.original_vision[i][1]
		
		self.hitbox = self.get_new_hitbox()
		self.vision_hitbox = self.get_new_vision_hitbox()

		# Limit some stuff
		self.acceleration[0] = 0
		self.rotational_acceleration = 0
		self.current_fitness = min([self.current_fitness, self.max_fitness])

		self.limit_position()
		
		if abs(self.velocity[0]) > self.max_velocity:
			self.velocity[0] = self.max_velocity*self.max_velocity/self.velocity[0]
		
		if abs(self.rotational_velocity) > self.max_rotational_velocity:
			self.rotational_velocity = self.max_rotational_velocity**2/self.rotational_velocity

		self.time_left_before_mating -= 1
		if self.time_left_before_mating < 0:
			self.time_left_before_mating = 0

		# This block is for energy consumption
		self.current_energy -= self.gene_dict["point_count"] # It should take more energy to maintain more points
		self.current_energy -= self.gene_dict["size"] # Being larger should cost more absolute energy
		self.current_energy -= abs(self.acceleration[0]) # Inertia
		self.current_energy -= abs(self.rotational_acceleration)
		self.current_fitness -= int(self.internal_temp)
		self.current_energy -= current_heat // Constants.ENVIRONMENT_SCALING
		self.current_energy -= (current_moisture // Constants.ENVIRONMENT_SCALING) // self.thinness

		self.time_left -= 1

		#self.total_loss = self.gene_dict["point_count"]+self.gene_dict["size"]+abs(self.acceleration[0])//2+abs(self.rotational_acceleration)//3
		
		if self.current_energy < 0:
			self.current_fitness += self.current_energy
			self.current_energy = 0

		elif self.current_energy >= self.max_energy:
			self.current_fitness += 1
			self.current_energy = self.max_energy
		
		if self.current_fitness < 0 or self.time_left < 0:
			self.die()

	def make_decision(self, objects_detected, occupied_tile_values):
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
		self.sensory_input[7] = self.internal_temp

		if len(objects_detected) > 0:
			self.object_detected = objects_detected[0]
			self.sensory_input[8] = objects_detected[0].get_size()
			self.sensory_input[9] = objects_detected[0].get_fitness_ratio()
			self.sensory_input[10] = objects_detected[0].get_colour()[0]
			self.sensory_input[11] = objects_detected[0].get_colour()[1]
			self.sensory_input[12] = objects_detected[0].get_colour()[2]
			self.sensory_input[13] = sqrt((self.get_position()[0]-objects_detected[0].get_position()[0])**2 + (self.get_position()[1]-objects_detected[0].get_position()[1])**2)
			self.sensory_input[14] = 1
			self.sensory_input[15] = objects_detected[0].gene_dict["point_count"]
		else:
			self.object_detected = None

		self.sensory_input[16] = occupied_tile_values[0]
		self.sensory_input[17] = occupied_tile_values[1]
		self.sensory_input[18] = occupied_tile_values[2]

		self.outputs = [0]*Constants.OUTPUT_NODES

		for i in range(len(self.hidden_layer)):
			self.hidden_layer[i] = sum([tanh(self.sensory_input[j]) * self.gene_dict["input_weights"][j] for j in range(Constants.INPUT_NODES)])

		for i in range(len(self.outputs)):
			self.outputs[i] = sum(tanh(self.hidden_layer[j]) * self.gene_dict["hidden_weights"][j] for j in range(Constants.HIDDEN_NODES))

		self.acceleration[0] = self.outputs[0] * self.gene_dict["output_weights"][0]
		self.rotational_acceleration = self.outputs[1] * self.gene_dict["output_weights"][1]
		self.mood = self.outputs[2] * self.gene_dict["output_weights"][2]

		if self.mood >= -1 and self.mood <= -0.8:
			self.aggression = True
			self.mating = False
			
		elif self.mood > -0.8 and self.mood < 0.8:
			self.aggression = False
			self.mating = False

		elif self.mood >= 0.8 and self.mood <= 1:
			self.aggression = False
			if not self.time_left_before_mating:
				self.mating = True

	def bump(self, magnitude):
		self.velocity[0] += magnitude
		self.velocity[1] *= 0.5

	def limit_position(self):
		if self.gene_dict["size"] < 1:
			print("WARNING: Size is ", self.gene_dict["size"])
		if self.position[0] < self.gene_dict["size"]:
			self.position[0] = self.gene_dict["size"]
		elif self.position[0] > Constants.MAP_WIDTH*Constants.ENVIRONMENT_ZONE_SIZE - self.gene_dict["size"]:
			self.position[0] = Constants.MAP_WIDTH*Constants.ENVIRONMENT_ZONE_SIZE - self.gene_dict["size"]
		if self.position[1] < self.gene_dict["size"]:
			self.position[1] = self.gene_dict["size"]
		elif self.position[1] > Constants.MAP_HEIGHT*Constants.ENVIRONMENT_ZONE_SIZE - self.gene_dict["size"]:
			self.position[1] = Constants.MAP_HEIGHT*Constants.ENVIRONMENT_ZONE_SIZE - self.gene_dict["size"]

	def generate_thinness(self):
		# Finds the distance between the two most distant points in the polygon
		# Finds the distance between the two second most distant points
		# Divides the two to get 'thinness'
		distances = []
		pairs = []
		for p in self.original_polygon:
			for p2 in self.original_polygon:
				tp = tuple(p)
				tp2 = tuple(p2)
				s = set([tp, tp2])
				if tp != tp2 and s not in pairs:
					dx = tp[0] - tp2[0]
					dy = tp[1] - tp2[1]
					distances.append(sqrt(dx**2 + dy**2))
					pairs.append(s)

		distances = sorted(distances, reverse=True)
		thinness = distances[0] / distances[1]

		return thinness

	def generate_perimeter(self):
		running_total_perimeter = 0
		for i in range(len(self.original_polygon)):
			dx = self.original_polygon[i-1][0] - self.original_polygon[i][0]
			dy = self.original_polygon[i-1][1] - self.original_polygon[i][1]
			distance = sqrt(dx**2 + dy**2)
			running_total_perimeter += distance

		return running_total_perimeter

	def draw(self, surface, offset):
		offset_polygon = [(p[0]-offset[0], p[1]-offset[1]) for p in self.polygon]
		offset_front_point = (self.front_point[0]-offset[0], self.front_point[1]-offset[1])
		offset_centre_point = (self.get_centre_point()[0]-offset[0], self.get_centre_point()[1]-offset[1])

		pygame.draw.polygon(surface, (self.gene_dict["colour"]), offset_polygon)
		pygame.draw.line(surface, (self.gene_dict["inverse_colour"]), offset_front_point, offset_centre_point)
		
		# Draws the organism's centre point (centre of bounding box)
		#pygame.draw.line(surface, self.gene_dict["inverse_colour"],
			#(self.get_centre_point()dTeV8sX+k,z\~AaFj~{Pl1RndTeV8sX+k,z\~AaFj~{Pl1Rn[0]-offset[0], self.get_centre_point()[1]-offset[1]), (self.get_centre_point()[0]-offset[0], self.get_centre_point()[1]-offset[1]))

		# Draws the organism's hitbox (bounding) for debug purposes
		#pygame.draw.rect(surface, (255, 0, 0), self.hitbox, 1)

		# And the vision triangle and hitbox
		#pygame.draw.polygon(surface, (0, 255, 255), self.vision, 1)
		#pygame.draw.rect(surface, (255, 0, 0), self.vision_hitbox, 1)

	def generate_polygon(self, initial_polygon):
		#print("new polygon")
		points = []

		if not initial_polygon:
			for p in range(self.gene_dict["point_count"]):
				points.append([randint(0, self.gene_dict["size"]), randint(0, self.gene_dict["size"])])
		else:
			for p in initial_polygon:
				points.append([p[0], p[1]])

		for p in range(self.gene_dict["point_count"] - len(points)): # Add new points if the organism happens to have mutated some
			points.append([randint(0, self.gene_dict["size"])+(random()*2 - 1) / 8, randint(0, self.gene_dict["size"])+(random()*2 - 1) / 8])

		# This loop fixes merged nodes
		for i in range(len(points)):
			for j in range(len(points)):
				if not points[i] is points[j]:
					while points[i] == points[j]:
						#print("fixing merger")
						points[j] = [randint(0, self.gene_dict["size"]), randint(0, self.gene_dict["size"])]

		self.gene_dict["point_count"] = len(points)

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
		self.gene_dict["colour"] = (0, 0, 0)
		self.dead = True

	def get_name(self):
		return self.name

	def get_id(self):
		return str(self.idname)

	def get_dead(self):
		return self.dead

	def get_hitbox(self):
		return self.hitbox

	def get_vision_hitbox(self):
		return self.vision_hitbox

	def get_hitbox_points(self):
		h = self.get_hitbox()
		return [(h[0], h[1]), (h[0]+h[2], h[1]), (h[0], h[1]+h[3]), (h[0]+h[2], h[1]+h[3])]

	def get_vision(self):
		return self.vision

	def get_new_vision_hitbox(self):
		return [
			min(p[0] for p in self.vision),
			min(p[1] for p in self.vision),
			max(p[0] for p in self.vision)-min(p[0] for p in self.vision),
			max(p[1] for p in self.vision)-min(p[1] for p in self.vision)]

	def get_vision_hitbox_points(self):
		h = self.get_vision_hitbox()
		return [(h[0], h[1]), (h[0]+h[2], h[1]), (h[0], h[1]+h[3]), (h[0]+h[2], h[1]+h[3])]

	def get_centre_point(self):
		# Bounding box centre
		b = self.get_hitbox()
		return (b[0] + b[2]/2, b[1]+ b[3]/2)

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

	def get_polygon(self):
		return self.polygon

	def get_original_polygon(self):
		return self.original_polygon

	def get_point_count(self):
		return self.gene_dict["point_count"]

	def get_object_detected(self):
		return self.object_detected

	def get_aggression(self):
		return self.aggression

	def get_mating(self):
		return self.mating

	def get_attack(self):
		return (abs(self.velocity[0])+abs(self.rotational_velocity)) // 2

	def get_velocity(self):
		return self.velocity

	def get_behaviour_bias(self):
		return self.gene_dict["behaviour_bias"]

	def get_temp_regulator(self):
		return self.gene_dict["temp_regulator"]

	def get_input_weights(self):
		return self.gene_dict["input_weights"]

	def get_hidden_weights(self):
		return self.gene_dict["hidden_weights"]

	def get_output_weights(self):
		return self.gene_dict["output_weights"]

	def get_inputs(self, weights=True):
		if weights:
			return [i*w for i,w in zip(self.sensory_input, self.get_input_weights())]
		return self.sensory_input

	def get_input_names(self):
		return self.input_names

	def get_hidden_layer(self, weights=True):
		if weights:
			return [h*w for h,w in zip(self.hidden_layer, self.get_hidden_weights())]
		return self.hidden_layer

	def get_outputs(self):
		# The weights have already been applied to these values
		return [self.acceleration[0], self.rotational_acceleration, self.mood]

	def get_mood_name(self):
		if self.aggression:
			return "Aggressive"
		elif self.mating:
			return "Reproductive"
		else:
			return "Neutral"

	def get_time_left_before_mating(self):
		return self.time_left_before_mating

	def get_reproduction_wait_period(self):
		return self.reproduction_wait_period

	def get_thinness(self):
		return self.thinness

	def get_perimeter(self):
		return self.perimeter

	def get_time_left(self):
		return self.time_left

	def shift_fitness(self, v):
		self.current_fitness += v

	def shift_energy(self, v):
		self.current_energy += v

	def set_mating(self, new_mating):
		self.mating = new_mating

	def set_time_left_before_mating(self, v):
		self.time_left_before_mating = v