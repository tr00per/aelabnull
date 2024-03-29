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
from threading import Thread

class Bezier:
    def __init__(self, height, width, p1p2=None):
        self.adaptation = 0.0
        self.__p0 = np.array( (0, height) )
        self.__p3 = np.array( (width, 0) )
        self.__width = width
        self.__height = height

        if p1p2 is None:
            self.__p1 = np.array( [r.random() * width, 2 * r.random() * height - height] )
            self.__p2 = np.array( [r.random() * width, 2 * r.random() * height - height] )
        else:
            self.__p1 = np.array(p1p2[0])
            self.__p2 = np.array(p1p2[1])

    def mutate(self):
        """Mutates by [-20%, 20%) for each coord"""
        coord = r.random()
        if coord < 0.25:
            self.__p1[0] += (r.random()*0.5-0.25) * self.__width
        elif coord < 0.5:
            self.__p1[1] += (r.random()*0.5-0.25) * self.__height
        elif coord < 0.75:
            self.__p2[0] += (r.random()*0.5-0.25) * self.__width
        else:
            self.__p2[1] += (r.random()*0.5-0.25) * self.__height
        # for fuck sake...
        #if self.__p1[0] < 0:
        #    self.__p1[0] = 0
        #if self.__p2[0] < 0:
        #    self.__p2[0] = 0

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
        return (1-x)**3 * self.__p0 + 3 * (1-x)**2 * x * self.__p1 \
            + 3 * (1-x) * x**2 * self.__p2 + x**3 * self.__p3

    def time(self, g = 9.81):
        """Inclined plane: a = g * sin(alpha) or a = g * (h/l)"""

        t = 0.0 # time
        v = 0.0 # speed

        oldAt = self.__at(0.0)
        for X in np.arange(0.02, 1.02, 0.02): #[0.02, 1.0]
            x1 = oldAt
            x2 = self.__at(X)
            oldAt = x2

            dx = x2 - x1
            #if dx[0] < 0:
                # oh no way, baby, no coming back
            #    return np.inf
            # dx[1] is negative when we go down, positive when up
            l = np.sqrt( np.vdot(dx, dx) ) # length
            h = -dx[1] # height

            dt = np.sqrt(2 * l * l / (g*np.abs(h)))
            a = g*(h/l) * dt
            v0 = v
            v += a # speed can increase or decrease here
            if v <= 0:
                # we have stopped
                return np.inf
            #t += 2*l / (v-v0)
            #t += l / ((v+v0)/2)
            t += dt

        return t

    def getVerts(self, codes=False):
        ret = [(self.__p0, self.__p1, self.__p2, self.__p3)]
        if codes:
            ret.append((Path.MOVETO, Path.CURVE4, Path.CURVE4, Path.CURVE4))
        return ret

class Population:
    def __init__(self, N, height, width, animated):
        self.__N = N
        self.__height = height
        self.__width = width
        self.__animate = animated
        self.__cnt = 0

        self.__pop = [ Bezier(self.__height, self.__width) for i in range(self.__N) ]
        self.__calcAdaptations(self.__pop)
        self.__pop.sort(key = lambda bez: bez.adaptation)
        print "Best at start:", round(self.__pop[0].adaptation, 8)

        if self.__animate > 0: #init plot animation
            self.__figure = plt.figure()
            self.__ax = self.__figure.add_subplot(111)

            textval = round(self.__pop[0].adaptation, 6)
            self.__text = self.__ax.text(-0.5*self.__width+0.5, 1.5*self.__height-1.0, textval, animated=True)

            self.__line, = self.__ax.plot([], [], 'x--', lw=2, color='black', ms=10, animated=True)

            verts, codes = self.__pop[0].getVerts(True)
            self.__patch = patches.PathPatch(Path(verts, codes), facecolor='none', lw=2, animated=True)
            self.__ax.add_patch(self.__patch)

            self.__ax.set_ylim(-0.5*self.__height, 1.5*self.__height)
            self.__ax.set_xlim(-0.5*self.__width, 1.5*self.__width)
            self.__ax.grid()

    def __calcAdaptations(self, target):
        for index in range(len(target)):
            target[index].adaptation = target[index].time()

    def nextEpoch(self, mutationChance, mateChance, maxEpoch=None):
        newPop = []
        origPop = self.__pop
        while len(newPop) < self.__N:
            if r.random() < mateChance:
                new1, new2 = self.__pop[0].mate(self.__pop[1])
                # remove at least one 'used' guy
                #self.__pop = self.__pop[1:] # __pop.pop()

                if r.random() < mutationChance: new1.mutate()
                if r.random() < mutationChance: new2.mutate()

                newPop.append(new1)
                newPop.append(new2)

                self.__pop[0].adaptation *= 1.2 #lower mating position by 20%
            else:
                new = self.__pop[0].clone()
                if r.random() < mutationChance: new.mutate()
                self.__pop = self.__pop[1:]
            self.__pop.sort(key = lambda bez: bez.adaptation)

        self.__pop = newPop # origPop + newPop
        self.__calcAdaptations(self.__pop)
        self.__pop.sort(key = lambda bez: bez.adaptation)
        self.__pop = self.__pop[:self.__N] #trim

        if self.__animate > 0 and (self.__cnt % self.__animate == 0 or self.__cnt == maxEpoch): #animate plot
            self.__figure.canvas.draw()

            verts, = self.__pop[0].getVerts()
            self.__patch.get_path().vertices = verts

            self.__ax.draw_artist(self.__patch)
            xs, ys = zip(*verts)
            self.__line.set_data(xs, ys)
            self.__ax.draw_artist(self.__line)

            self.__text.set_text(round(self.__pop[0].adaptation, 6))
            self.__ax.draw_artist(self.__text)

            self.__figure.canvas.blit(self.__ax.bbox)

            self.__cnt += 1

        return [ bez.adaptation for bez in self.__pop ]

    def show(self, which=0):
        if self.__animate > 0: return #do not use both

        verts, codes = self.__pop[which].getVerts(True)
        path = Path(verts, codes)

        fig = plt.figure()
        ax = fig.add_subplot(111)
        patch = patches.PathPatch(path, facecolor='none', lw=2)
        ax.add_patch(patch)

        xs, ys = zip(*verts)
        ax.plot(xs, ys, 'x--', lw=2, color='black', ms=10)

        ax.text(verts[0][0]+0.05, verts[0][1]+0.05, 'P0')
        ax.text(verts[1][0]+0.05, verts[1][1]+0.05, 'P1')
        ax.text(verts[2][0]+0.05, verts[2][1]+0.05, 'P2')
        ax.text(verts[3][0]+0.05, verts[3][1]+0.05, 'P3')

        ax.set_xlim(-0.5*self.__width, 1.5*self.__width)
        ax.set_ylim(-0.5*self.__height, 1.5*self.__height)
        plt.show()

def run():
    print "Oh! Bezier is evolving!"
    pop = []
    for i in range(MaxIter):
        pop = run.population.nextEpoch(run.mutate, run.mate, run.maxI)
        print i, "epoch's best:", round(pop[0], 6)
        #print np.round(pop, 2)
    print "Bezier has evolved into Brachistochrone!"
    print "Best of last epoch:", round(pop[0], 8)

if __name__ == "__main__":
    N = 40
    Height = 5
    Width = 20
    MaxIter = 50
    MutationChance = 0.3
    MateChance = 0.9
    Animation = 0
    opts, args = go.getopt(sys.argv[1:], "n:w:h:i:p:m:M:a:A")
    for opt, arg in opts:
        if opt == "-n":
            N = int(arg)
        elif opt == "-w":
            Width = float(arg)
        elif opt == "-h":
            Height = float(arg)
        elif opt == "-i":
            MaxIter = int(arg)
        elif opt == "-m":
            MutationChance = float(arg)
        elif opt == "-M":
            MateChance = float(arg)
        elif opt == "-a":
            Animation = int(arg)
        elif opt == "-A":
            Animation = 1

    print "Creating population..."
    run.population = Population(N, Height, Width, Animation)
    run.mutate = MutationChance
    run.mate = MateChance
    run.maxI = MaxIter

    if Animation > 0:
        thr = Thread(target=run)
        thr.start()
        plt.show()
    else:
        run()
        run.population.show()
