"""
A breadth first search walker
"""

from collections import deque
from maze_constants import *
import walker_base
from maze_pieces import MazeError

class SearchColors(object):
    """An object that will generate the gray cyclic pattern used by
    breadth-first search
    """
    colors = ['gray80', 'gray78', 'gray76', 'gray74', 'gray72', 'gray70', \
              'gray68', 'gray66', 'gray64', 'gray62', 'gray60']

    def __init__(self):
        assert len(SearchColors.colors) > 1
        self.index = 0
        self.step = 1

    def color(self):
        return SearchColors.colors[self.index]

    def next(self):
        if self.index == len(SearchColors.colors) - 1:
            self.step = -1
        elif self.index == 0:
            self.step = 1
        self.index += self.step


SEARCH_COLORS = SearchColors()
FOUND_COLOR = 'red3'
marker = object()

class BreadthWalker(walker_base.WalkerBase):

    class Node(object):
        __slots__ = 'previous'

        def __init__(self):
            self.previous = None

    def __init__(self, maze):
        super(BreadthWalker, self).__init__(maze, maze.start(), self.Node())
        self._maze.clean()
        self.queue = deque()
        self.queue.append(self._cell)
        self.queue.append(marker)

    def step(self):
        current = self.queue.popleft()

        if current is marker:
            self.queue.append(marker)
            SEARCH_COLORS.next()            
            
        elif current is self._maze.finish():
            while current is not None:
                # Start cell should point to None
                self._maze.paint(current, FOUND_COLOR)
                current = self.read_map(current).previous
            self._isDone = True
        else:
            self._maze.paint(current, SEARCH_COLORS.color())            
            
            for next in current.get_paths(last=self.read_map(current).previous):
                if self.read_map(next).previous is None:
                    self.read_map(next).previous = current
                    self.queue.append(next)
            self.step()
