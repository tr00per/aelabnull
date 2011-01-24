# -*- coding: utf-8 -*-

from node import Node
import numpy as np

class Population:
    def __init__(self, n, maxEpoch, x_from, x_to, target):
        self.MAXEPOCH = maxEpoch
        self.FROM = x_from
        self.TO = x_to
        self.STEP = np.abs(x_to - x_from) * 0.05 #21 control points
        self.TARGET = self.__calc_values(target)

        self.POP = [self.random_individual() for i in range(n)]

    def __calc_values(self, specimen):
        ret = []
        for x in np.arange(self.FROM, self.TO+self.STEP, self.STEP):
            try:
                ret.append(specimen.calc(x))
            except ZeroDivisionError:
                ret.append(np.inf)
        return np.array(ret)

    def __calc_diffs(self):
        #FIXME calc differentials
        return [ self.__calc_values(specimen) for specimen in self.POP ]

    def epoch(self):
        newPop = []
        diffs = self.__calc_diffs

        for i in range(len(diffs)):
            diffs[i] = np.abs(diffs[i]).sum()

        best = np.array(diffs).argsort()

        #FIXME now what...?

    def random_individual(self):
        return Node.random_node(0)
