"""
Constant values for the maze program

"""

import sys

DELAY = 5   # milliseconds
G_DELAY = 1
G_INDIVIDUAL = 20
G_GEN0_STEPS = 30

CELL_SIZE = 20      # pixels
# includes space for walls, so subtract 2 ultimately

#trap constants
T_ON = 'black'
T_OFF = 'yellow'

XCELLS = 30
YCELLS = 30
MAZE_HEIGHT = YCELLS * CELL_SIZE + 1
MAZE_WIDTH = XCELLS * CELL_SIZE + 1
if XCELLS * YCELLS > sys.getrecursionlimit():
    sys.setrecursionlimit(XCELLS * YCELLS)

# Colors
NULL_FILL = 'forest green'
PLAN_FILL = 'grey'
OPEN_FILL = 'black'
DOT_COLORS = ['green', 'red']   # start dot, finish dot
G_SOLVED_PATH = 'red3'

# Helpers
DIRECTIONS = ['north', 'east', 'south', 'west']
OPPOSITES = {'north': 'south', 'east': 'west', 'south': 'north', \
             'west': 'east'}


