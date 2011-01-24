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

    def __calc_values(self, target):
        ret = []
        for x in np.arange(self.FROM, self.TO+self.STEP, self.STEP):
            try:
                ret.append(target.calc(x))
            except ZeroDivisionError:
                ret.append(np.inf)
        return np.array(ret)

    def __calc_diffs(self, x):
        #FIXME calc differentials
        ret = []
        for specimen in self.POP:
            pass

    def random_individual(self):
        return Node.random_node(0)
