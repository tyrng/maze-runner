#!/usr/bin/python

"""
The class file for the maze, as well as the cells within the maze.

"""

from textwrap import fill
import Tkinter as Tk
from maze_constants import *
from maze_pieces import Hall, Cell
from wilson import Wilson
from depth_walker import DepthWalker
from breadth_walker import BreadthWalker
from astar_walker import aStarWalker
from deadend_filler import DeadendFiller
from tremaux import Tremaux
from mouse import RandomMouse
from genetic_algorithm import *
import random
import sys

class Maze(Tk.Canvas):

    def __init__(self, frame):
        #Genetic Algorithm trigger
        self.gAlgorithm = ''
        self.solvedPath = []
        self.individualSolved = False
        self.count = 0

        self._frame = frame
        self._cells = [[Cell(x, y) for y in xrange(YCELLS)] \
                       for x in xrange(XCELLS)]
        for x in xrange(XCELLS-1):
            for y in xrange(YCELLS):
                self._link(self._cells[x][y], 'east', self._cells[x+1][y])
        for x in xrange(XCELLS):
            for y in xrange(YCELLS-1):
                self._link(self._cells[x][y], 'south', self._cells[x][y+1])

        Tk.Canvas.__init__(self, self._frame, height=MAZE_HEIGHT, \
                           width=MAZE_WIDTH, background='black', \
                           highlightthickness=0)

        self.pack()

        for column in self._cells:
            for cell in column:
                self._plot_cell(cell)
                if self._is_congruent(cell):
                    self._plot_walls(cell)

        for cell, color in zip([self.start(), self.finish()], DOT_COLORS):
            self.create_oval(*self._cell_bounds(cell), fill=color, \
                               tag='dots', outline='')

        self.lift('corners')
        self.lower('dots')
        self.update_idletasks()
        self.prompt_build()


    def memory_summary(self):
        # Only import Pympler when we need it. We don't want it to
        # affect our process if we never call memory_summary.
        from pympler import summary, muppy
        mem_summary = summary.summarize(muppy.get_objects())
        rows = summary.format_(mem_summary)
        return '\n'.join(rows)

    def _run(self):     #runs solution
        if not self._walker.is_done():
            self._walker.step()
            self.after(self._walker.delay(), self._run)
        else:
            self.lift('dots')
            print (self.memory_summary())
            if(self.gAlgorithm == '1' or self.gAlgorithm == '2'):
                self.g_prompt()
            else:
                self.prompt()

    def gen_run(self):     #runs solution
        if not self._walker.is_done():
            self._walker.step()
            self.after(G_DELAY, self.gen_run())
        else:
            self.lift('corners')
                
    #Runs genetic algorithm                
    def g_run(self):
        if not self._walker.is_done():
            self._walker.step()
            self.after(self._walker.delay(), self.g_run())
        else:
            self.lift('dots')        
            self.gen_loop()                

    def prompt_build(self):
        """Get user input before the maze has been built"""
        factor = raw_input("Enter loop factor (0: No loops; 100: All loops): ")
        print "How much of the maze building would you like to see?"
        print "1: Show me everything"
        print "2: Just give me the broad strokes"
        print "3: Quick Generation"
        try:
            speed = int(raw_input(">> "))
        except ValueError:
            print "Since you can't type, I can only assume you're in a hurry."
            speed = 3
        print 'Building...'
        self._walker = Wilson(self, float(factor) / 100.0, speed)       #maze generation
        self.after(self._walker.delay(), self._run)


    #path finding for dead end filler run
    def g_prompt(self):
        if(self.gAlgorithm == '1' or self.gAlgorithm == '2'):
            if (self.gAlgorithm == '2'):
                self.gAlgorithm = '' 
                self._walker = getAllPaths(self)
                self.after(self._walker.delay(), self.g_run())
            else:
                self.gAlgorithm = ''
                self.gen_loop()  
                     
            
    #Genetic algorithm loop        
    def gen_loop(self):
        self.generation = 0
        gen_state = False
        #loop here   
        #       
        walkClass = Gen_algorithm
            
        self._walker = walkClass(self)

        while(gen_state == False):
            print "Generation: " + str(self.generation)
            self.generation = self.generation + 1

            #self.cleanPath(G_SOLVED_PATH)        

            self.after(G_DELAY, self.gen_run())
                
            if self.individualSolved:
                gen_state = True
                break
            
            self._walker.updateAllFitness()
            
            self._walker.selection_crossover()
            
            const = random.randint(1,2)

            # self._walker.mutation()

            if (const == 2):
                self._walker.mutation()

            self._walker.prepareNextGen()
        
        

        self.individualSolved = False
        self.prompt()
                
            


    def prompt(self):

        """Get user input after the maze has been built"""
           
        classes = {'d': DepthWalker, 'b': BreadthWalker, 'f': DeadendFiller, '2': DeadendFiller, \
                   't': Tremaux, 'm': RandomMouse, 'a': aStarWalker, '1': aStarWalker}
        while True:
            print "Choose maze solving algorithm"
            print "(D)epth first search"
            print "(B)readth first search"
            print "(A) star search"
            print "(1). Genetic A star search"
            print "Deadend (f)iller"
            print "(2). Genetic Deadend filler"
            print "(T)remaux's algorithm"
            print "Random (m)ouse"
            print "(R)ebuild maze"        
            print "(Q)uit"
            
            
            choice = raw_input(">> ").strip().lower()
            
            
            if choice == '1' or choice == '2':
                self.gAlgorithm = choice 

            if choice == 't':
                self.solvedPath = []
            
            if choice == 'q':
                raise SystemExit
            elif choice == 'r':
                self.rebuild()
                return            
            try:
                #import pdb; pdb.set_trace()
                walkClass = classes[choice]
                
            except KeyError:
                continue

            break

        self._walker = walkClass(self)
        self.after(self._walker.delay(), self._run)     #Run solution

    def rebuild(self):
        """Clean and rebuild the maze"""
        self.count=0
        del self.solvedPath[:]
        
        self.lower('dots')
        for column in self._cells:
            for cell in column:
                for hall in cell.get_halls():
                    hall.close_wall()
                self.paint(cell, NULL_FILL)
        self.update_idletasks()
        self.prompt_build()

    def _is_congruent(self, cell):
        """This will make a checkerboard pattern for checking cell walls, so
        we aren't drawing the same wall twice
        """
        x, y = cell.get_position()
        return (x % 2) == (y % 2)

    def _plot_cell(self, cell):
        """Make a rect on the canvas the size of a cell, and set the cell's
        tk id.
        """
        topLeft, bottomRight = self._cell_bounds(cell)
        cell.set_id(self.create_rectangle(topLeft, bottomRight, \
                                          fill=NULL_FILL, outline=NULL_FILL))

    def _cell_bounds(self, cell):
        """Return the a tuple of the top left and bottom right corners of the
        cell object suitable for drawing.
        """
        x, y = cell.get_position()
        topLeft = (x * CELL_SIZE + 1, y * CELL_SIZE + 1)
        bottomRight = (topLeft[0] + CELL_SIZE - 2, topLeft[1] + CELL_SIZE - 2)
        return topLeft, bottomRight

    def _plot_walls(self, cell):
        """Plot the four walls for a cell and set the hall tk ids."""
        x, y = cell.get_position()
        x = (x * CELL_SIZE)
        y = (y * CELL_SIZE)

        topLeft = (x, y)                    #WTF 8 points
        bottomLeft = (x, y + CELL_SIZE)
        topRight = (x + CELL_SIZE, y)
        bottomRight = (x + CELL_SIZE, y + CELL_SIZE)
        corners = [topLeft, topRight, bottomRight, bottomLeft]
        for corner in corners:
            self.create_rectangle(corner, corner, fill=NULL_FILL, \
                                  tag='corners', outline='')

        wallCoords = [(corners[i], corners[(i + 1) % 4]) for i in xrange(4)]
        for direction, pair in zip(DIRECTIONS, wallCoords):
            hall = cell.get_hall(direction)
            if hall is not None:
                hall.set_id(self.create_line(pair, fill=NULL_FILL))

    def _link(self, cellA, direction, cellB):
        """Build a hallway between cellA and cellB. Direction is A -> B."""
        hall = Hall(cellA, cellB)
        cellA.add_hall(direction, hall)
        cellB.add_hall(OPPOSITES[direction], hall)

    def get_cell(self, x, y):
        """Returns the cell at position x, y.
        x and y are in terms of cell numbers, not pixels"""
        return self._cells[x][y]

    def get_maze_array(self):
        """Return the entire array; useful for certain walking functions"""
        return self._cells

    def clean(self):
        """Return every cell to a default color"""
        self.count = 0
        for col in self._cells:
            for cell in col:
                self.paint(cell, OPEN_FILL)
        self.update_idletasks()

    def cleanPath(self, color):
        """Reprint solved path"""
        for cell in self.solvedPath:
            self.paint(cell, color)
        self.update_idletasks()    

    def cleanDot(self, color):
        """Reprint dot"""
        for dot in self.solvedPath:
            if dot == self.start() or dot == self.finish():
                continue
            x,y = dot.get_position()
            self.paint_individual(x, y, color)
        self.update()    

    def paint(self, cell, color, paintWalls=True):          #color
        """Takes a cell object and a color to paint it.
        Color must be something that Tkinter will recognize."""
        self.itemconfigure(cell.get_id(), fill=color, outline=color)
        self.update()
        # Paint the walls
        if paintWalls:
            for hall in cell.get_halls():
                if hall.is_open():  # The wall is down
                    fillColor = color
                else:
                    fillColor = NULL_FILL
                self.itemconfigure(hall.get_id(), fill=fillColor) 
                   
    def Wpaint(self, cell, color, paintWalls=True):          #color
        """Takes a cell object and a color to paint it.
        Color must be something that Tkinter will recognize."""
        self.itemconfigure(cell.get_id(), fill=color, outline=color)
        # Paint the walls
        if paintWalls:
            for hall in cell.get_halls():
                if hall.is_open():  # The wall is down
                    fillColor = color
                else:
                    fillColor = NULL_FILL
                self.itemconfigure(hall.get_id(), fill=fillColor) 

    #check color of each cell 
    def check_color(self, cell, paintWalls=True):
        return self.itemcget(cell.get_id(), 'fill')
        
    #Mark individuals (oval shape)
    def paint_individual(self, x, y, color):        
        
        topLeft = (x * CELL_SIZE + 1, y * CELL_SIZE + 1)
        bottomRight = (topLeft[0] + CELL_SIZE - 2, topLeft[1] + CELL_SIZE - 2)
        corners = [topLeft, bottomRight]        
        
        self.create_oval(corners, fill=color, outline=color)
        self.update()

    def start(self):
        return self._cells[0][0]

    def finish(self):
        return self._cells[XCELLS-1][YCELLS-1]

if __name__ == '__main__':
    root = Tk.Tk()
    root.title('Maze Game Group 5')
    maze = Maze(root)
    root.mainloop()

