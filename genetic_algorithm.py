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
                print current
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
        self.fitness = 0.00000000
        self.steps = 0
        self.genes = []        
        self.current_location = self._maze.start()
        self.color = color
        self.moves = DIRECTIONS    
        self.distance = 0.000000000 
        for x in range(gene_length):
            self.genes.append(random.choice(self.moves))
                        

class Gen_algorithm(walker_base.WalkerBase):
    """Genetic algorithm class"""    

    def __init__(self, maze):
        super(Gen_algorithm, self).__init__(maze, maze.start())        
        self._delay = G_DELAY
        self.gene_length = 20       #steps for each individual
        self.population = [Individual(self._maze, self.gene_length, individual_color[x]) for x in range(10)]
        self.fittest = None
        self.secondFit = None
        self.fittestG = []
        self.secondFittestG = []
        self.leastFittest = []
        self.currentStep = 0
            
    def step(self):
        if self.currentStep < self.gene_length:
            self._maze.cleanDot(G_SOLVED_PATH)
            for individual in self.population:
                move = self._cell.move_individual(self._maze, individual.current_location, individual.genes[self.currentStep])
                # print individual.color + ' ' + str(individual.steps)
                if move is not None:
                    individual.current_location = move
                    individual.steps = individual.steps + 1
                x,y = individual.current_location.get_position()
                self._maze.paint_individual(x, y, individual.color)
            self.currentStep = self.currentStep + 1
        else:
            self._isDone = True
            self.updateAllFitness()
            for individual in self.population:
                print individual.color + ' ' + str(individual.fitness)
    
    def calDistance(self, cell):
        cell.distance = 0.0000000 + len(self._maze.solvedPath) - self._maze.solvedPath.index(cell)
        
    def updateAllFitness(self):
        for individual in self.population:
            distance = self.calDistance(individual.current_location)
            individual.fitness = individual.distance + (individual.distance / individual.steps)
    
    def updateFitness(self, individual):
        distance = self.calDistance(individual.current_location)
        individual.fitness = individual.distance + (individual.distance / individual.steps)

    def prepareNextGen(self):
        if self.fittest.distance / self.gene_length >= 0.70:
            new_gene_length = self.gene_length * 2
            diff = new_gene_length - self.gene_length
            for x in range(diff):
                self.genes.append(random.choice(self.moves))
            
    def getFittest(self):
        pq = Q.PriorityQueue()
        
    
        for x in self.population:
            pq.put((100/x.fitness),x)
        
        self.fittest = pq.get()
        self.secondFit = pq.get()          
            
    def selection_crossover(self):               
        self.getFittest()
        
        self.fittestG = fittest.genes
        self.secondFittestG= secondFit.genes
        
        for x in pq:
            if not pq.empty():
                lastFit = pq.get()
        
        for x in self.population:
            if x == lastFit:
                x.genes = self.fittestG
        
        #crossover
        crossOverPoint = random.randint(1, self.gene_length)
        
        for x in range(crossOverPoint):
            temp = self.fittestG[x]
            self.fittestG[x] = self.secondFittestG[x]
            self.secondFittestG[x] = temp
            
        for x in self.population:
            if x == fittest:
                x.genes = self.fittestG
            elif x == secondFit:
                x.genes = self.secondFittestG
                
    
    def mutation(self):
        
        
            
        
        
    
