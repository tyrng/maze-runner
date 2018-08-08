"""
An A* search walker
"""

import Queue as Q
from maze_constants import *
import walker_base
from maze_pieces import MazeError

VISITED_COLOR = 'gray20'
FOUND_COLOR = G_SOLVED_PATH
# marker = object()

class aStarWalker(walker_base.WalkerBase):

    class Node(object):
        __slots__ = 'previous'

        def __init__(self):
            self.previous = None

    def __init__(self, maze):
        super(aStarWalker, self).__init__(maze, maze.start(), self.Node())
        self._maze.clean()
        self.queue = Q.PriorityQueue()
        self.queue.put((0, self._cell))
        # self.queue.put(marker, 1)
        self.cost_so_far = {}
        self.cost_so_far[self._cell] = 0

    def step(self):
        currentCost, current = self.queue.get()

        if current is self._maze.finish():
            
            while current is not None:
                # Start cell should point to None
                self._maze.paint(current, FOUND_COLOR)
                self._maze.solvedPath.append(current)
                current = self.read_map(current).previous
            self._isDone = True
        else:
            self._maze.paint(current, VISITED_COLOR)
            for next in current.get_paths(last=self.read_map(current).previous):
                if self.read_map(next).previous is None:
                    new_cost = self.cost_so_far[current] + 1
                    if (next not in self.cost_so_far) or (new_cost < self.cost_so_far[next]):
                        self.cost_so_far[next] = new_cost
                        priority = new_cost + self.heuristic(self._maze.finish(), next)
                        self.read_map(next).previous = current
                        self.queue.put((priority, next))
