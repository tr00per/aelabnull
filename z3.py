#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import numpy as np
import math as m
import random as rand
import matplotlib.pyplot as plot
import getopt as go

class Bezier:
    def __init__(self, height, width, p1p2=None):
        self.adaptation = 0.0
        self.__p0 = np.array( (0, height) )
        self.__p3 = np.array( (width, 0) )

        if p1p2 is None:
            self.__p1 = np.array( [2 * rand.random() * width - width, 2 * rand.random() * height - height] )
            self.__p2 = np.array( [2 * rand.random() * width - width, 2 * rand.random() * height - height] )
        else:
            self.__p1 = np.array(p1p2[0])
            self.__p2 = np.array(p1p2[1])

    def mutate(self):
        """Mutates by [-20%, 20%) for each coord"""
        self.__p1[0] *= r.random() * 0.4 + 0.8 #[0.8, 1.2)
        self.__p1[1] *= r.random() * 0.4 + 0.8
        self.__p2[0] *= r.random() * 0.4 + 0.8
        self.__p2[1] *= r.random() * 0.4 + 0.8

    def mate(self, other, wX=0.3, wY=0.3):
        """Returns touple of two children. wX & Wy = [0, 1]"""
        rwX = 1 - wX
        rwY = 1 - wY

        coords = ()
        one = Bezier(self.__height, self.__width, coords)

        coords = ()
        two = Bezier(self.__height, self.__width, coords)

        return one, two

    def clone(self):
        return Bezier(height, width, (self.__p1, self.__p2))

    def getPoints():
        return (self.__p0, self.__p1, self.__p2, self.__p3)

    def __at(self, x):
        """x = [0, 1]"""
        return (1-x)**3 * self.__p0 + 3 * ((1-x)**2) * x * self.__p1 \
            + 3 * (1-x) * (x**2) * self.__p2 + (x**3) * self.__p3

    def time(self, g = 9.81):
        """t = l / sqrt(2 * g * h)"""
        sqrt2g = 1.0 / np.sqrt(2 * g)
        ret = 0.0
        oldX = 0.0
        for X in np.arange(0.01, 1, 0.01):
            v1 = self.__at(oldX)
            v2 = self.__at(X)

            v = v2 - v1
            l = np.sqrt( (v ** 2).sum() ) # length
            h = np.abs(v1[1] - v2[1]) #height

            ret += l * sqrt2g / np.sqrt(h)
            oldX = X

        return ret

class Population:
    def __init__(self, N, height, width):
        self.__N = N
        self.__height = height
        self.__width = width

        self.__pop = [ Bezier(self.__height, self.__width) for i in range(self.__N) ]
        self.__calcAdaptations()

    def __calcAdaptations(self):
        for index in range(self.__N):
            self.__pop[index].adaptation = self.__pop[index].time()

    def nextEpoch(self, mutationChance, mateChance):
        newPop = []

        while len(newPop) < self.__N:
            self.__pop.sort(key = lambda bez: bez.adaptation)

            if r.random() < mateChance:
                new1, new2 = self.__pop[0].mate(self.__pop[1])

                if r.random() < self.__mutate: new1.mutate()
                if r.random() < self.__mutate: new2.mutate()

                newPop.append(new1)
                newPop.append(new2)

                self.__pop[0].adaptation *= 1.2 #lower mating position by 20%
            else:
                newPop.append(self.__pop[0].clone())
                self.__pop[0].adaptation = float("Inf") #disable mating

        self.__pop = newPop[:self.__N]
        self.__calcAdaptations()
        print [ bez.adaptation for bez in self.__pop ]

    def show():
        #draw plot
        pass

    def getPop():
        return toupe(self.__pop)

if __name__ == "__main__":
    N = 40
    Height = 10
    Width = 20
    MaxIter = 100
    Pecision = 10
    MutationChance = 0.2
    MateChance = 0.9
    opts, args = go.getopt(sys.argv[1:], "n:w:h:i:p:m:M:")
    for opt, arg in opts:
        if opt == "-n":
            N = int(arg)
        elif opt == "-w":
            Width = int(arg)
        elif opt == "-h":
            Height = int(arg)
        elif opt == "-i":
            MaxIter = int(arg)
        elif opt == "-p":
            Precision = float(arg)
        elif opt == "-m":
            MutationChance = float(arg)
        elif opt == "-M":
            MateChance = float(arg)

    population = Population(N, Height, Width)

    for i in range(MaxIter):
        population.nextEpoch(MutationChance, MateChance)
        #if population.getPop()[0].adaptation <= Precision: break

    #print "Best:", population.getPop()[0].adaptation
