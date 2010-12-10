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
        self.begin = (0, height)
        self.end = (width, 0)
        self.p0 = [2 * rand.random() * width - width, 2 * rand.random() * height - height]
        self.p1 = [2 * rand.random() * width - width, 2 * rand.random() * height - height]

    def mutate(self):
        pass

    def mate(self, other):
        pass

    def _at(self, x):
        """x = [0, 1]"""
        return (1-x)**3 * self.begin + 3 * (1-x)**2 * x * self.p0 \
            + 3 * (1-x) * x**2 * self.p1 + x**3 * self.end

    def time(self, g = 9.81):
        """t = l / sqrt(2 * g * h)"""
        pass

if __name__ == "__main__":
    N = 30
    opts, args = go.getopt(sys.args[1:], "N:")
    for opt, arg in opts:
        if opt == "-N":
            N = int(arg)

    population = []

    print "Hello world!"
