#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import numpy as np
import math as m
import random as rand
import matplotlib.pyplot as plot
import getopt as go

class Bezier:
    def __init__(self, height, width):
        self.__p0 = (0, height)
        self.__p1 = [2 * rand.random() * width - width, 2 * rand.random() * height - height]
        self.__p2 = [2 * rand.random() * width - width, 2 * rand.random() * height - height]
        self.__p3 = (width, 0)
        self.adaptation = 0.0

    def mutate(self):
        pass

    def mate(self, other):
        pass

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
            v1 = np.array((oldX, self.__at(oldX)))
            v2 = np.array((X, self.__at(X)))

            v = v2 - v1
            l = np.sqrt( (v ** 2).sum() ) # length
            h = np.abs(v1[1] - v2[1]) #height

            ret += l * sqrt2g / np.sqrt(h)
            oldX = X

        return ret

class Population:
    def __init__(self, N, height, width, mutationChance):
        self.__N = N
        self.__height = height
        self.__width = width
        self.__mutate = mutationChance

        self.__pop = [ Bezier(self.__height, self.__width) for i in range(self.__N) ]

    def __calcAdaptations(self):
        for index in range(self.__N):
            self.__pop[index].adaptation = self.__pop[index].time()

    def nextEpoch(self):
        self.__calcAdaptations()
        self.__pop.sort(key = lambda bez: bez.adaptation)

        print [ bez.adaptation for bez in self.__pop ]

    def show():
        #draw plot
        pass

if __name__ == "__main__":
    N = 40
    Height = 10
    Width = 20
    MaxIter = 100
    Precision = 0.8
    MutationChance = 0.2
    opts, args = go.getopt(sys.argv[1:], "n:w:h:i:p:m:")
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

    population = Population(N, Height, Width, MutationChance)

    for i in range(MaxIter):
        population.nextEpoch()

    print "Hello world!"
