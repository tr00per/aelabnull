# -*- coding: utf-8 -*-

from consts import *
import math
import numpy as np
import random as r

class OperatorException(Exception):
    def __init__(self, which):
        self.value = "Unrecognized operator: " + which

    def __str__(self):
        return repr(self.value)

class ChildException(Exception):
    def __init__(self, where):
        self.value = "Bad number of children @ " + where

    def __str__(self):
        return repr(self.value)

class Node:
    def __init__(self, value):
        """Operators are things that are not floats. Validated later
        Two-argument operators: +, -, *, /, **
        One-argument operators: sin, cos, tan, sqrt and so on (math module)
        Actual list:
        """
        self.__allowed_operators = legal_two
        self.__operator = False
        self.__first = None
        self.__second = None
        self.__variable = None

        self.__value = str(value).strip()

        try:
            testVar = float(self.__value)
        except ValueError:
            if self.__value == 'x':
                self.__variable = 'x'
            elif self.__value in legal_other:
                self.__variable = 'np.' + self.__value #depends on numpy as np module import!
            else:
                self.__operator = True

    def addChild(self, child):
        if self.__first is None:
            self.__first = child
            return

        if self.__second is None:
            self.__second = child
            return

        raise ChildException("child addition")

    def calc(self, x):
        if self.__operator:
            if self.__first is None: #has at least one child?
                raise ChildException("none children given for operator " + self.__value)

            if self.__value in legal_two:
                if self.__second is None:
                    raise ChildException("too few children for operator " + self.__value)
                try:
                    left = str(self.__first.calc(x))
                except ZeroDivisionError:
                    left = "0.0"
                else:
                    if left == "inf" or left == "nan":
                        left = "np."+left
                    elif left == "-inf":
                        left = "-np.inf"

                try:
                    right = str(self.__second.calc(x))
                except ZeroDivisionError:
                    right = "np.inf" #depends on numpy as np module import!
                else:
                    if right == "inf" or right == "nan":
                        right = "np."+right
                    elif right == "-inf":
                        right = "-np.inf"

                try:
                    return str(eval(left + self.__value + right))
                except ArithmeticError:
                    raise ZeroDivisionError
                except ValueError:
                    raise ZeroDivisionError

            elif self.__value in legal_one:
                if self.__second is not None:
                    raise ChildException("too many children for operator " + self.__value)
                try:
                    arg = str(self.__first.calc(x))
                except ZeroDivisionError:
                    arg = "np.inf" #depends on numpy as np module import!
                else:
                    if arg == "inf" or arg == "nan":
                        arg = "np."+arg
                    elif arg == "-inf":
                        arg = "-np.inf"

                try:
                    return str(eval("math." + self.__value + "(" + arg + ")" )) #depends on math module import!
                except ArithmeticError:
                    raise ZeroDivisionError
                except ValueError:
                    raise ZeroDivisionError

            else:
                raise OperatorException(self.__operator)

        elif self.__variable is not None:
            return x
        else:
            return self.__value

    def __str__(self):
        """For pretty printing of a tree. No validation! And LISPish appearance."""
        if self.__operator:
            ret = "(" + self.__value + " " + str(self.__first)
            if self.__second is not None:
                ret += " " + str(self.__second)
            return ret + ")"
        else:
            return self.__value

    def swap(self, other):
        """Low-level mate.
        Swaps values and children of given nodes."""
        tmp['val'] = self.__value
        tmp['first'] = self.__first
        tmp['sec'] = self.__second

        self.__value = other.__value
        self.__first = other.__first
        self.__second = other.__second

        other.__value = tmp['val']
        other.__first = tmp['first']
        other.__second = tmp['sec']

    def mutate(self):
        """Modify random thing"""
        choice = r.random()
        if choice < 0.3334: #change operator/value
            if self.__operator:
                if self.__second is not None: #change operator
                    self.__value = r.choice(legal_two)
                else:
                    self.__value = r.choice(legal_one)
            else:
                if self.__variable is not None:
                    self.__value += self.__value * (3 * r.random() - 2) #-200% + 100%
                #hope that unneeded variables and constants will get whiped by surrounding

        elif choice < 0.6667: #change subnode
            if self.__second is not None:
                which = r.random()
                if which < 0.5:
                    self.__second.mutate()
                    return
            self.__first.mutate()
            pass

        else: #change whole node
            tmp = Node.random_node(r.randint(0, 100), 100)

    def __random_subnode(self):
        """Pick a subnode randomly. Avoid root."""
        if r.random() < 0.5:
            pick = self.__first
        else:
            pick = self.__second

        while r.random() < 0.667:
            # go deeper
            left = (r.random() < 0.5)
            if (left and pick.__first) or (not left and pick.__second):
                pick = pick.__first if left else pick.__second
            else:
                break
        return pick

    def copulate(self, partner):
        node1 = self.__random_subnode()
        node2 = partner.__random_subnode()
        node1.swap(node2) # i'm sensing a fuckup. we should clone them, shouldn't we? FIXME
        return [node1, node2]

    @staticmethod
    def random_node(level, max_level=100):
        """Generate random tree"""
        _operators = legal_two
        _leaves = ['x', 'e', 'x', 'pi', 'x', 'x']
        _leaves.extend(np.arange(-10, 10, 1))
        _functions = legal_one

        _oper_probability = Node.oper_probability / (level+1.0); # the deeper, the more leaves
        _func_probability = _oper_probability * 0.6
        _leaf_probability = 1 - (_oper_probability + _func_probability)

        chance = r.random()
        if level >= max_level: #fail-safe
            chance = 1
        if chance < _oper_probability:
            # new operator
            node = Node(r.choice(_operators))
            node.addChild(Node.random_node(level+1))
            node.addChild(Node.random_node(level+1))
        elif chance < (_oper_probability + _func_probability):
            # new function
            node = Node(r.choice(_functions))
            node.addChild(Node.random_node(level+1))
        else:
            # new leaf
            return Node(r.choice(_leaves))
        return node

Node.oper_probability = 1.0
