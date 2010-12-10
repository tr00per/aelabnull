#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import numpy as np
import math as m
import random as r
import matplotlib.pyplot as plt
from matplotlib.path import Path
import matplotlib.patches as patches
import getopt as go

class Bezier:
    def __init__(self, height, width, p1p2=None):
        self.adaptation = 0.0
        self.__p0 = np.array( (0, height) )
        self.__p3 = np.array( (width, 0) )

        if p1p2 is None:
            self.__p1 = np.array( [r.random() * width, 2 * r.random() * height - height] )
            self.__p2 = np.array( [r.random() * width, 2 * r.random() * height - height] )
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
        """Returns touple of two children. wX & Wy = (0, 1)"""
        rwX = 1 - wX #r - reverse
        rwY = 1 - wY

        coords = (self.__p1 * wX + other.__p1 * rwX, self.__p2 * wY + other.__p2 * rwY)
        one = Bezier(self.__p0[1], self.__p3[0], coords)

        coords = (self.__p1 * rwX + other.__p1 * wX, self.__p2 * rwY + other.__p2 * wY)
        two = Bezier(self.__p0[1], self.__p3[0], coords)

        return one, two

    def clone(self):
        return Bezier(self.__p0[1], self.__p3[0], (self.__p1, self.__p2))

    def getPoints():
        return (self.__p0, self.__p1, self.__p2, self.__p3)

    def __at(self, x):
        """x = [0, 1]; from Wikipedia"""
        return (1-x)**3 * self.__p0 + 3 * ((1-x)**2) * x * self.__p1 \
            + 3 * (1-x) * (x**2) * self.__p2 + (x**3) * self.__p3

    def time(self):
        """ inclined plane: a = g * sin(alpha)
        or a = g * (h/l)

        We ignore the g in the calculations to simplify stuff.
        It's included at the end."""

        t = 0.0 # time
        v = 0.0 # speed

        oldX = 0.0
        for X in np.arange(0.02, 1.02, 0.02):
            x1 = self.__at(oldX)
            x2 = self.__at(X)

            dx = x2 - x1
            l = np.sqrt( np.vdot(dx, dx) ) # length
            h = - dx[1] #height

            a = (h/l)
            v += a # speed can increase or decrease here
            if v <= 0:
                # we have stopped
                return np.inf
            t += l / v

            oldX = X

        return t

    def show(self):
        verts = [self.__p0, self.__p1, self.__p2, self.__p3]
        codes = [Path.MOVETO, Path.CURVE4, Path.CURVE4, Path.CURVE4]
        path = Path(verts, codes)

        fig = plt.figure()
        ax = fig.add_subplot(111)
        patch = patches.PathPatch(path, facecolor='none', lw=2)
        ax.add_patch(patch)

        xs, ys = zip(*verts)
        ax.plot(xs, ys, 'x--', lw=2, color='black', ms=10)

        ax.text(self.__p0[0]+0.05, self.__p0[1]+0.05, 'P0')
        ax.text(self.__p1[0]+0.05, self.__p1[1]+0.05, 'P1')
        ax.text(self.__p2[0]+0.05, self.__p2[1]+0.05, 'P2')
        ax.text(self.__p3[0]+0.05, self.__p3[1]+0.05, 'P3')

        ax.set_xlim(-self.__p3[0], 1.5*self.__p3[0])
        ax.set_ylim(-self.__p0[1], 1.5*self.__p0[1])
        plt.show()

class Population:
    def __init__(self, N, height, width):
        self.__N = N
        self.__height = height
        self.__width = width

        self.__pop = [ Bezier(self.__height, self.__width) for i in range(self.__N) ]
        self.__calcAdaptations(self.__pop)
        self.__pop.sort(key = lambda bez: bez.adaptation)

    def __calcAdaptations(self, target):
        for index in range(self.__N):
            target[index].adaptation = target[index].time()

    def nextEpoch(self, mutationChance, mateChance):
        newPop = []

        while len(newPop) < self.__N:
            if r.random() < mateChance:
                new1, new2 = self.__pop[0].mate(self.__pop[1])

                if r.random() < mutationChance: new1.mutate()
                if r.random() < mutationChance: new2.mutate()

                newPop.append(new1)
                newPop.append(new2)

                self.__pop[0].adaptation *= 1.2 #lower mating position by 20%
            else:
                newPop.append(self.__pop[0].clone())
                self.__pop[0].adaptation = float("Inf") #disable mating
            self.__pop.sort(key = lambda bez: bez.adaptation)

        self.__pop = newPop[:self.__N]
        self.__calcAdaptations(self.__pop)
        self.__pop.sort(key = lambda bez: bez.adaptation)

        return [ bez.adaptation for bez in self.__pop ]

    def show(self, which=0):
        self.__pop[which].show()

if __name__ == "__main__":
    N = 40
    Height = 10
    Width = 20
    MaxIter = 50
    Precision = 0.1
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

    print "Creating population..."
    population = Population(N, Height, Width)

    print "Oh! Bezier is evolving!"
    pop = []
    for i in range(MaxIter):
        pop = population.nextEpoch(MutationChance, MateChance)
        print i, "epoch's best:", pop[0]
        print np.round(pop, 2)
        if pop[0] <= Precision:
            print "Precision reached!"
            break
    print "Bezier has evolved into Brachistochrone!"

    print "Best of last epoch:", pop[0] / 9.81, "s"
    population.show()
