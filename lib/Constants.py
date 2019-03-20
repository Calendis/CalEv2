# Some constants that are vital to the simulation

STARTING_POPULATION = 300
POPULATION_LIMIT = 600
POPULATION_MINIMUM = 300
REPRODUCTION_WAIT_PERIOD = 10

INPUT_NODES = 19
HIDDEN_NODES = 11
OUTPUT_NODES = 3

ORGANISM_LIFESPAN = 12000 # All organisms get an equal share of time, in frames

REPRODUCTION_COST_MULTIPLIER = 20
EAT_GAIN_MULTIPLIER = 2

ENVIRONMENT_ZONE_SIZE = 60

# Sets the energy per tile. A tile will usually start with about a fifth of this value
# You could set this lower for a more difficult environment or higher for a more leniant one
# This also provides the max passive energy value for a tile
ENVIRONMENT_SCALING = 10000

REPLENISH_DIVISOR = 24 # A higher value means that the nutrient-regen map will have smaller values

QUADTREE_CAPACITY = 2

MAP_WIDTH = 100
MAP_HEIGHT = 60