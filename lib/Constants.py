# Some constants that are vital to the simulation

STARTING_POPULATION = 250
POPULATION_LIMIT = 600
POPULATION_MINIMUM = 200
REPRODUCTION_WAIT_PERIOD = 1

INPUT_NODES = 19
HIDDEN_NODES = 11
OUTPUT_NODES = 3

ORGANISM_LIFESPAN = 5500 # All organisms get an equal share of time, in frames
ORGANISM_TOUGHNESS = 12

REPRODUCTION_COST_MULTIPLIER = 16
EAT_GAIN_MULTIPLIER = 40

ENVIRONMENT_ZONE_SIZE = 60

# Sets the energy per tile. A tile will usually start with about a fifth of this value
# You could set this lower for a more difficult environment or higher for a more leniant one
# This also provides the max passive energy value for a tile
ENVIRONMENT_SCALING = 7500
HEATMAP_MULTIPLER = 0.2 # The heatmap is a strong, so we weaken it

# Times in seconds
MAP_REFRESH_DELAY = 0.5
RESPAWN_DELAY = 10

REPLENISH_DIVISOR = 25 // MAP_REFRESH_DELAY # A higher value means that the nutrient-regen map will have smaller values

QUADTREE_CAPACITY = 4

MAP_WIDTH = 100
MAP_HEIGHT = 60
