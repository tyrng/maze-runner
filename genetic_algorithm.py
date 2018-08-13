# -*- coding: utf-8 -*-
"""GENETIC ALGORITHM CLASS"""

from collections import deque
import random
import walker_base
from maze_constants import *
import Queue as Q


marker = object()


class getAllPaths(walker_base.WalkerBase):
    """An walker that will trace all posssible paths"""
    class Node(object):
        __slots__ = 'previous'

        def __init__(self):
            self.previous = None

    def __init__(self, maze):
        super(getAllPaths, self).__init__(maze, maze.start(), self.Node())    
        self.queue = deque()
        self.queue.append(self._cell)
        self.queue.append(marker)

    def step(self):
        
        
        current = self.queue.popleft()

        if current is marker:
            self.queue.append(marker)            
        elif current is self._maze.finish():
            while current is not None:
                # Start cell should point to None
                self._maze.paint(current, G_SOLVED_PATH)
                
                #test shape                       
                #    
                #store in solvedPath
                self._maze.solvedPath.append(current)
                
                current = self.read_map(current).previous                
            self._isDone = True
        else:
            color = self._maze.check_color(current) #get color            
            for next in current.get_bPaths(color, last=self.read_map(current).previous):
                if self.read_map(next).previous is None:
                    self.read_map(next).previous = current
                    self.queue.append(next)
            self.step()


#Color of the individuals
individual_color = ['cyan3', 'spring green', 'goldenrod', 'dark violet', 'magenta2', 'snow2', 'DarkSeaGreen2', 'hot pink', 'LightSalmon2', 'RoyalBlue3']              

class Individual(walker_base.WalkerBase):
    def __init__(self, maze, gene_length, color):
        super(Individual, self).__init__(maze, maze.start())
        #dead status
        self.dead = False
        self.fitness = 0.00000000
        self.steps = 0
        self.genes = []        
        self.current_location = self._maze.start()
        self.color = color
        self.moves = DIRECTIONS
        self.eachDistance = 0.000000000 
        self.distance = 0.000000000 
#        self.stay = 0
#        self.back = 0
        for x in xrange(0,gene_length,1):
            self.genes.append(random.choice(self.moves))
                        

class Gen_algorithm(walker_base.WalkerBase):
    """Genetic algorithm class"""    

    def __init__(self, maze):
        super(Gen_algorithm, self).__init__(maze, maze.start())  
        #TrapCellList
        self.trapCellList = []        
        
        self._delay = G_DELAY
        self.gene_length = G_GEN0_STEPS       # gen 0 steps for each individual
        self.population = [Individual(self._maze, self.gene_length, individual_color[x%10]) for x in xrange(0,G_INDIVIDUAL)]
        self.fittest = None
        self.secondFit = None
        self.fittestG = []
        self.secondFittestG = []
        self.leastFittest = []
        self.currentStep = 0
        self.oldBestFit = [] # Premature Convergence
        
        self.oldDead = 0
            
    def step(self):
        if self.currentStep < self.gene_length:
            #DELETION
            for d in self._maze.dotList:
                if d is not None:
                    self._maze.delete(d)
            
            self._maze.dotList = [] 
           
            #self._maze.cleanDot(G_SOLVED_PATH)      #CLEAN DOT REPLACEMENT
            for individual in self.population:                                             
                if(individual.dead):
                    move = None
                else:
                    move = self._cell.move_individual(self._maze, individual.current_location, individual.genes[self.currentStep])                
                
                if move is not None:
                    individual.current_location = move
                    individual.steps = individual.steps + 1
                    
                    for trap in self.trapCellList:
                        if(individual.current_location == trap):
                            if(self._maze.tStatus):
                                individual.dead = True                                
                   
#                else:
#                    individual.stay = individual.stay + 1
                x,y = individual.current_location.get_position()
                self._maze.paint_individual(x, y, individual.color)
                if individual.current_location == self._maze.finish():
                    self._maze.individualSolved = True
                    self.currentStep = self.gene_length
                    break
            self.currentStep = self.currentStep + 1
        else:
            self._isDone = True
                
    def printTable(self):
        averageFitness = 0
        averageDistance = 0
        print '#' + ' : ' + ' D. ' + ' : ' + 'Fitness'
        for x in self.population:
            print str(self.population.index(x)) + ' : ' + str(x.distance) + ' : ' + "%.2f" % x.fitness
            averageFitness = averageFitness + x.fitness / len(self.population)
            averageDistance = averageDistance + x.distance / len(self.population)
            
        print '==========================================='
        print 'AVERAGE DISTANCE = ' + "%.2f" % (averageDistance)
        print 'AVERAGE FITNESS  = ' + "%.2f" % (averageFitness)
        print 'Fittest Score    = ' + "%.2f" % (self.fittest.fitness)
        print '==========================================='

    def calDistance(self, individual):
        s = list(self._maze.solvedPath)
        s.reverse()
        individual.distance = 0.0000000 + s.index(individual.current_location)
        
    def updateAllFitness(self):
        for individual in self.population:
            self.calDistance(individual)
            if individual.steps == 0:
                individual.fitness = -1
            else:
                #FITNESS SCORE PENALTY
                if(individual.dead):
                    penalty = 1
                else:
                    penalty = 0
                individual.fitness = individual.distance + (individual.distance / individual.steps) - penalty
            if individual.fitness < 0:
                individual.genes = []
                for x in xrange(0,self.gene_length):
                    individual.genes.append(random.choice(individual.moves))

    def prepareNextGen(self):
        for x in self.population:
            x.current_location = self._maze.start()
#            x.stay = 0
            x.steps = 0
#            x.back = 0
            
        self._isDone = False
        self.currentStep = 0
        #GENE LENGTH UPDATE
        if self.fittest.distance / self.gene_length >= 0.35:
            new_gene_length = self.gene_length + 10
            # new_gene_length = self.gene_length + G_GEN0_STEPS
            diff = new_gene_length - self.gene_length
            self.gene_length = new_gene_length
            for individual in self.population:
                for x in xrange(0,diff):
                    individual.genes.append(random.choice(individual.moves))
            
    def getFittest(self):
        pq = Q.PriorityQueue()
        
    
        for x in self.population:
            if x.fitness <= 0:
                x.fitness = 1.0
            pq.put((100/x.fitness,x))
            if x.fitness == 1.0:
                x.fitness = -1.0
        
        nn1, self.fittest = pq.get()
        nn2, self.secondFit = pq.get()   

        for x in xrange(0,G_INDIVIDUAL):
            if not pq.empty():
                nn3, self.lastFit = pq.get()
            else:
                break       
            
    def selection_crossover(self):               
        #self.getFittest()
        
        self.fittestG = []
        self.secondFittestG = []
        self.fittestG = list(self.fittest.genes)
        self.secondFittestG= list(self.secondFit.genes)
        
        
        # for x in self.population:
        #     if x == self.lastFit:
        #         x.genes = []
        #         x.genes = self.fittestG
        
        self.lastFit.genes = []
        self.lastFit.genes = list(self.fittestG)

        #crossover
        crossOverPoint = random.randint(0, self.gene_length*3/4)
        # crossOverPoint = self.gene_length / 2 - 1
        
        for x in xrange(0,crossOverPoint,1):
            temp = self.fittestG[x]
            self.fittestG[x] = self.secondFittestG[x]
            self.secondFittestG[x] = temp
            
        # for x in self.population:
        #     if x == self.fittest:
        #         x.genes = []
        #         x.genes = self.fittestG
        #     elif x == self.secondFit:
        #         x.genes = []
        #         x.genes = self.secondFittestG

        self.fittest.genes = []
        self.fittest.genes = list(self.fittestG)
        self.secondFit.genes = []
        self.secondFit.genes = list(self.secondFittestG)
                
    def prematureConvergence(self):
        self.getFittest()
        self.oldBestFit.append(self.fittest) # float        
        
        if len(self.oldBestFit) >= 3: # check at least 3 generations
            one = self.oldBestFit.pop()
            two = self.oldBestFit.pop()
            three = self.oldBestFit.pop()                        
                
            
            if (one.fitness == two.fitness and two.fitness == three.fitness and one.fitness == three.fitness):                                    
                self.oldBestFit = []
                #DEAD STOPPER
                if(one.dead == True and two.dead == True and three.dead == True):
                    return None
                
                # ADD GENE_LENGTH
                diff = 10
                new_gene_length = self.gene_length + diff
                self.gene_length = new_gene_length
                for individual in self.population:
                    for x in xrange(0,diff):
                        individual.genes.append(random.choice(individual.moves))

            else:
                self.oldBestFit.append(three)
                self.oldBestFit.append(two)
                self.oldBestFit.append(one)

    def mutation(self):
        
        mutationPoint1 = random.randint(0, self.gene_length-1)
        mutationPoint2 = random.randint(0, self.gene_length-1)
        
        #self.getFittest()
        #========================================================Fittest mutation
        self.fittestG = []
        self.fittestG = list(self.fittest.genes)
        self.secondFittestG = []
        self.secondFittestG = list(self.secondFit.genes)      
        
        
        temp = self.fittestG[mutationPoint1]
        self.fittestG[mutationPoint1] = self.fittestG[mutationPoint2]  
        self.fittestG[mutationPoint2] = temp
        #=========================================================Second Fittest mutation
        
        mutationPoint1 = random.randint(0, self.gene_length-1)
        mutationPoint2 = random.randint(0, self.gene_length-1)        
        
        temp = self.secondFittestG[mutationPoint1]
        self.secondFittestG[mutationPoint1] = self.secondFittestG[mutationPoint2]  
        self.secondFittestG[mutationPoint2] = temp
         
        for x in self.population:
            if x == self.fittest:
                x.genes = []
                x.genes = list(self.fittestG)
            elif x == self.secondFit:
                x.genes = []
                x.genes = list(self.secondFittestG)
    
    #SUPER MUTATION ===========================================================
    def superMutation(self):
        notDead = False
        
        for x in self.population:
            if(x.dead == False):
                notDead = True
        
        if(notDead == False):
            
            superPercentage = self.gene_length * 0.2
            
            for individual in self.population:                            
                
                for x in xrange(0,int(superPercentage)): 
                    r1 = random.randint(self.gene_length/2, self.gene_length-1)
                    individual.genes[r1] = random.choice(individual.moves)
                    
            return True
        
        return False
    
    #TRAP FUNCTIONS
    def setTrap(self, status, randomG):
        
        count = 0        
                
        if(self._maze.tStatus):
            color = T_ON
            op_color = T_OFF
        else:
            color = T_OFF
            op_color = T_ON
        
        for x in self._maze.solvedPath:
            if(randomG == count):
                self._maze.printTrap(x._xLoc, x._yLoc, color, op_color)
                self.trapCellList.append(x)
            elif((randomG - 2) == count):
                self._maze.printTrap(x._xLoc, x._yLoc, color, op_color)
                self.trapCellList.append(x)
                                                
            count = count + 1
            
        
            
        
        
    
