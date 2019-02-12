# Code concerning the environment that the organisms will interact with
from noise import pnoise2
from random import random, randint
from lib import UI
from lib import Constants

default_islands = {"intensity": 1, "sea_level": 0}
valleys = {"intensity": 0.5, "sea_level": -0.2}
fjords = {"intensity": 2, "sea_level": -0.1}
ridges = {"intensity": 1.2, "sea_level": -0.3}
plains = {"intensity": 0.2, "sea_level": -0.17}
spires = {"intensity": 6, "sea_level": 0.6}

current_preset = plains

def generate_noisemap(width, height, intensity=current_preset["intensity"], sea_level=current_preset["sea_level"], complete_randomize=False, scramble=False):
	heightmap = []
	#map_seed = randint(1,20)*randint(1,1000000) #Perlin noise is not chaotic, so similar seeds will produce similar maps
	map_seed = randint(-10000, 10000)

	map_size = 7
	octaves = 8 #Detail level of the map

	#Sets up the heightmap as a nice 2D list
	for i in range(width):
		heightmap.append([])
	for i in range(width):
		for j in range(height):
			heightmap[i].append([])

	#Generates perlin noise and adds it to the heightmap
	for i in range(width):
		i_2 = map_seed + i
		for j in range(height):
			j_2 = map_seed + j
			heightmap[i][j] = pnoise2((i_2*map_size)/width, (j_2*map_size)/height, octaves, 0.1, 2, 1024, 1024)
	
	#Operates on the heightmap based on perameters
	for i in range(width):
		for j in range(height):
			
			heightmap[i][j] *= intensity
			heightmap[i][j] -= sea_level
			heightmap[i][j] = max(0, heightmap[i][j]) # No negative values please

			heightmap[i][j] *= Constants.ENVIRONMENT_SCALING

			if complete_randomize:
				intensity = randint(-30,30)/10
				sea_level = randint(-4,4)/10
			
			#Scrambler
			if scramble:
				if not randint(0, 3):
					heightmap[i][j] = heightmap[int(i/randint(1,4))][j]


	return heightmap

def get_colour(v):
	return tuple([int(min(255, max(v/Constants.ENVIRONMENT_SCALING, 0)*255))]*3)