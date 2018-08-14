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
import time

class Maze(Tk.Canvas):

    def __init__(self, frame):
        #trap status
        self.trapList = []
        self.tCount = 0
        self.tStatus = False
        
        #List of individual dots
        self.dotList = []
        
        self.gAlgorithm = ''
        self.solvedPath = []
        self.individualSolved = False
        self.count = 0
        self.successPath = []

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


    def _run(self):     #runs solution
        if not self._walker.is_done():
            self._walker.step()
            self.after(self._walker.delay(), self._run)
        else:
            self.lift('dots')            
            if(self.gAlgorithm == 'a' or self.gAlgorithm == 'f'):
                self.g_prompt()
            else:
                self.prompt()

#GEN RUN=======================================================================

    def gen_run(self):     #runs solution
        #TRAP SWITCH
        if(self.tCount == 0):
            #delete trap list
            for x in self.trapList:
                if x is not None:
                    self.delete(x)            
                
            #set count back to 3 (delay)
            self.tCount = 4
            if(self.tStatus == False):
                self.tStatus = True
            elif(self.tStatus == True):
                self.tStatus = False
            #create trap object
            self.trapList = []
            self._walker.trapCellList = []
            
            self._walker.setTrap(self.tStatus, self.randomG)
            
        
        self.tCount = self.tCount - 1
        #===========
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
        if(self.gAlgorithm == 'f' or self.gAlgorithm == 'a'):
            if (self.gAlgorithm == 'f'):
                self.gAlgorithm = '' 
                self._walker = getAllPaths(self)
                self.after(self._walker.delay(), self.g_run())                    
            else:
                self.gAlgorithm = ''      
        
        print "Enter Genetic algorithm? (y/n): "
        
        choice = raw_input(">> ").strip().lower()
        
        if (choice == 'y'):
            self.gen_loop()  
        else:
            self.prompt()
                     
            
    #Genetic algorithm loop        
    def gen_loop(self):
        self.generation = 0
        gen_state = False
        #loop here   
        #       
        walkClass = Gen_algorithm
            
        self._walker = walkClass(self)

        #Mutation variation        
        mutationRate = 2
        oldGeneLength = self._walker.gene_length
        
        self.randomG = random.randint(1, len(self.solvedPath)-2)
        
        while(gen_state == False):
            #Reset back dead status
            self.tStatus = False            
            
            for x in self._walker.population:
                x.furthestDistance = 0 
                x.deadSteps = 0
                x.dead = False
            #======================
            print '///////////////////////////////////////////'
            print "Generation: " + str(self.generation)
            print '///////////////////////////////////////////'
            self.generation = self.generation + 1

            #self.cleanPath(G_SOLVED_PATH)        

            self.after(DELAY, self.gen_run())

            self._walker.updateAllFitness()
            self._walker.getFittest()       #get Fittest here
            self._walker.printTable()
            
            
            #mutation experiment            
            newGeneLength = oldGeneLength + 20
            if(newGeneLength <= self._walker.gene_length):
                mutationRate = mutationRate + 1
                oldGeneLength = newGeneLength
                            
            
            const = random.randint(1, mutationRate) # print const
            mutation = False
            if (const == 2):
                print 'MUTATION      : ON'
                mutation = True
            else:
                print 'MUTATION      : OFF'
                mutation = False
                
            
            print 'MUTATION RATE : ' + "%.2f" % ((1.00/mutationRate) * 100.00) + '%'
            print '==========================================='            
            
                
            if self.individualSolved:
                gen_state = True
                break
            
            
            self._walker.selection_crossover()
            

            # self._walker.mutation()

            if (mutation):
                for x in xrange(0, self._walker.gene_length, 5):
                    self._walker.mutation()
                            #SUPER MUTATION                    
                if(self._walker.superMutation()):
                    # ADD GENE_LENGTH
                    diff = 10
                    new_gene_length = self._walker.gene_length + diff
                    self._walker.gene_length = new_gene_length
                    for individual in self._walker.population:
                        for x in xrange(0,diff):
                            individual.genes.append(random.choice(individual.moves))
                    print 'SUPER MUTATION: ON'
                else:
                    print 'SUPER MUTATION: OFF'
            else:
                 print 'SUPER MUTATION: OFF'
            
            print '==========================================='   
            print 'GENE LENGTH: ' + str(self._walker.gene_length)

            
            self._walker.prematureConvergence()
            

            self._walker.prepareNextGen()
        
        

        self.individualSolved = False
        self.prompt()
                
            


    def prompt(self):

        """Get user input after the maze has been built"""
           
        classes = {'d': DepthWalker, 'b': BreadthWalker, 'f': DeadendFiller, \
                   't': Tremaux, 'm': RandomMouse, 'a': aStarWalker}
        while True:
            print "Choose maze solving algorithm"
            print "(D)epth first search"
            print "(B)readth first search"
            print "(A) star search"
            print "Deadend (f)iller"
            print "(T)remaux's algorithm"
            print "Random (m)ouse"
            print "(R)ebuild maze"        
            print "(Q)uit"
            
            
            choice = raw_input(">> ").strip().lower()
            
            
            if choice == 'f' or choice == 'a':
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
        #CLEAR ALL DOTS AND TRAPS
        for x in self.trapList:
                if x is not None:
                    self.delete(x)   
                    
        for d in self.dotList:
                if d is not None:
                    self._maze.delete(d)
        
        
        """Clean and rebuild the maze"""
        self.count=0
        del self.solvedPath[:]
        del self.successPath[:]
        
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
        del self.successPath[:]
        for col in self._cells:
            for cell in col:
                self.paint(cell, OPEN_FILL)
        self.update_idletasks()

    def cleanPath(self, color):
        """Reprint solved path"""
        for cell in self.solvedPath:
            self.paint(cell, color)
        for cell in self.successPath:
            if cell not in self.solvedPath:
                self.paint(cell, OPEN_FILL)
        del self.successPath[:]
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
        
        dot = self.create_oval(corners, fill=color, outline=color)   #DOTLIST STORED HERE
        self.dotList.append(dot)
        
        self.update()

    #create trap object========================================================
    def printTrap(self, x, y, color, op_color):
        
        
#        topLeft = (x * CELL_SIZE + 1, y * CELL_SIZE + 1)
#        bottomRight = (topLeft[0] + CELL_SIZE - 2, topLeft[1] + CELL_SIZE - 2)  
#        
#        midTopLine = [bottomRight[0]/ 2, topLeft[1]]
#        midBotLine = [bottomRight[0]/ 2, bottomRight[1]]
#        midLeftLine = [topLeft[0], bottomRight[1]/ 2]
#        midRightLine = [bottomRight[0], bottomRight[1]/ 2]
        
        top = [(x * CELL_SIZE) + ((CELL_SIZE + 1)/ 2), (y * CELL_SIZE + 1)]
        right = [(x * CELL_SIZE) + CELL_SIZE - 1, (y * CELL_SIZE) + ((CELL_SIZE + 1)/ 2)]
        bottom = [(x * CELL_SIZE) + ((CELL_SIZE + 1)/ 2), (y * CELL_SIZE) + CELL_SIZE - 1]
        left = [(x * CELL_SIZE + 1), (y * CELL_SIZE) + ((CELL_SIZE + 1)/ 2)]
        
        #self.trapList.append(self.create_polygon(midLeftLine, midTopLine, midRightLine, midBotLine, fill=color, outline=op_color))
        self.trapList.append(self.create_polygon(left, top, right, bottom, fill=color, outline=op_color))
            
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

