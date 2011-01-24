# -*- coding: utf-8 -*-

from node import Node
import numpy as np
import random as r

class Population:
    def __init__(self, n, x_from, x_to, target):
        self.FROM = x_from
        self.TO = x_to
        self.STEP = np.abs(x_to - x_from) * 0.05 #21 control points
        self.TARGET = self.__calc_values(target)
        self.N = n
        self.POP = [self.random_individual() for i in range(n)]

    def __calc_values(self, specimen,  delta=0.0):
        ret = []
        for x in np.arange(self.FROM, self.TO + self.STEP, self.STEP):
            ret.append(specimen.calc(x+delta))
        ret = np.array(ret)
        print ret.shape
        print len(ret)
        print ret
        return ret

    def __calc_diffs(self):
        """Calc differentials"""
        delta = 0.001
        dx = 2 * delta
        diffs = []
        for specimen in self.POP:
            values = self.__calc_values(specimen,  delta)
            values -= self.__calc_values(specimen,  -delta)
            values /= dx
            #for x in np.arange(self.FROM, self.TO + self.STEP, self.STEP):
            #    dy = float(specimen.calc(x + delta)) - float(specimen.calc(x - delta))
            #    values.append( dy/dx )
            diffs.append(values)
        return diffs

    def epoch(self):
        # some parameters:
        p_crossing = 0.8
        p_mutation = 0.1

        newPop = []
        diffs = self.__calc_diffs()

        for i in range(len(diffs)):
            diffs[i] = np.abs(diffs[i] - self.TARGET).sum()

        best = np.array(diffs).argsort().tolist()

        parents = []
        idx = 0
        while len(newPop) < self.N:
            if r.random() < p_crossing:
                parents.append(self.POP[best.pop(idx)])
                idx -= 1 # will increase back to current value...
                if len(parents) == 2:
                    # BREED!
                    children = parents[0].copulate(parents[1])
                    newPop += children
                    parents = []
            else:
                # maybe mutate if not breeding?
                if r.random() < p_mutation:
                    self.POP[best[idx]].mutate()
            idx += 1
            if idx >= len(best):
                idx = 0

        self.POP = newPop

    def random_individual(self):
        return Node.random_node(0)
