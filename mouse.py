"""
A random mouse class for the maze. (Regular method)

"""

from random import choice
from maze_constants import *
from walker_base import WalkerBase

MOUSE_COLOR = 'brown'     #Mouse color (try to randomize for genetic algorithm)
                
class RandomMouse(WalkerBase):

    def __init__(self, maze):
        super(RandomMouse, self).__init__(maze, maze.start())
        self._maze.clean()
        self._last = None
        self._delay = 50        #DELAY USED TO MEASURE TIME EFFICIENCY OF EACH CODE

    def step(self):
        if self._cell is self._maze.finish():
            self._isDone = True
            return

        paths = self._cell.get_paths(last=self._last)

        if len(paths) == 0:
            # We've hit a deadend
            self._cell, self._last = self._last, self._cell
        else:
            self._last = self._cell
            self._cell = choice(paths)

        self.paint(self._cell, MOUSE_COLOR)
        self.paint(self._last, OPEN_FILL)