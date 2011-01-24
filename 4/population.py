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
        self.N = n
        self.POP = [self.random_individual() for i in range(n)]

    def __calc_values(self, specimen):
        ret = []
        for x in np.arange(self.FROM, self.TO + self.STEP, self.STEP):
            try:
                ret.append(specimen.calc(x))
            except ZeroDivisionError:
                ret.append(np.inf)
        return np.array(ret)

    def __calc_diffs(self):
        #FIXME calc differentials
        delta = 0.001
        dx = 2 * delta
        diffs = []
        for specimen in self.POP:
            values = []
            for x in np.arange(self.FROM, self.TO + self.STEP, self.STEP):
                dy = specimen.calc(x + delta) - speciment.calc(x - delta)
                #dx = 2 * delta
                # i feel a strange urge to use numpy somehwere here
                values.append( dy/dx )
            diffs.append(values)
        return diffs
        # oh fck it.
        # return [ self.__calc_values(specimen) for specimen in self.POP ]

    def epoch(self):
        # some parameters:
        p_crossing = 0.8
        p_mutation = 0.1

        newPop = []
        diffs = self.__calc_diffs

        for i in range(len(diffs)):
            diffs[i] = np.abs(diffs[i]-self.TARGET).sum()

        best = np.array(diffs).argsort()

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
            if idx > len(best):
                idx = 0

        self.POP = newPop


    def random_individual(self):
        return Node.random_node(0)
