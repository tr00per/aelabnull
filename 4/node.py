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

        if self.__value == 'x':
            self.__variable = 'x'
        elif self.__value in legal_other:
            self.__variable = 'np.' + self.__value #depends on numpy as np module import!
        else:
            try:
                testVar = float(self.__value)
            except ValueError:
                self.__operator = True
            else:
                self.__value = testVar

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

                left = str(self.__first.calc(x))
                if left == "inf" or left == "nan":
                    left = "np."+left
                elif left == "-inf":
                    left = "-np.inf"

                right = str(self.__second.calc(x))
                if right == "inf" or right == "nan":
                    right = "np."+right
                elif right == "-inf":
                    right = "-np.inf"

                try:
                    if self.__value == '**':
                        return eval('math.pow('+left+','+right+')')
                    else:
                        return eval(left + self.__value + right)
                except ArithmeticError:
                    return np.inf
                except ValueError:
                    return np.inf

            elif self.__value in legal_one:
                if self.__second is not None:
                    raise ChildException("too many children for operator " + self.__value)
                arg = str(self.__first.calc(x))
                if arg == "inf" or arg == "nan":
                    arg = "np."+arg
                elif arg == "-inf":
                    arg = "-np.inf"

                try:
                    return eval("math." + self.__value + "(" + arg + ")" ) #depends on math module import!
                except ArithmeticError:
                    return np.inf
                except ValueError:
                    return np.inf

            else:
                raise OperatorException(self.__operator)

        elif self.__variable is not None:
            return eval(self.__variable)
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
            return str(self.__value)

    def swap(self, other):
        """Low-level mate.
        Swaps values and children of given nodes."""
        tmp = {
            'val' : self.__value,
            'first' : self.__first,
            'sec' : self.__second,
            'oper' : self.__operator,
            'var' : self.__variable
        }

        self.__value = other.__value
        self.__first = other.__first
        self.__second = other.__second
        self.__operator = other.__operator
        self.__variable = other.__variable

        other.__value = tmp['val']
        other.__first = tmp['first']
        other.__second = tmp['sec']
        other.__operator = tmp['oper']
        other.__variable = tmp['var']

    def clone(self):
        sibling = Node(self.__value)
        if self.__first is not None:
            sibling.addChild(self.__first.clone())
        if self.__second is not None:
            sibling.addChild(self.__second.clone())
        return sibling

    def __mutate_value(self):
        if self.__operator:
            if self.__second is not None: #change operator
                self.__value = r.choice(legal_two)
            else:
                self.__value = r.choice(legal_one)
        else:
            if self.__variable is None:
                self.__value += self.__value * (3 * r.random() - 2) #-200% + 100%
            #hope that unneeded variables and constants will get whiped by surrounding

    def __mutate_subnode(self):
        if self.__second is not None:
            which = r.random()
            if which < 0.5:
                self.__second.mutate()
                return
        self.__first.mutate()

    def __mutate_all(self):
        tmp = Node.random_node(r.randint(0, 49))
        self.swap(tmp)

    def mutate(self):
        """Modify random thing"""
        choice = r.random()
        if choice < 0.3334:     #change operator/value
            self.__mutate_value()

        elif choice < 0.6667:   #change subnode
            if self.__first is not None:
                self.__mutate_subnode()
            else:           #there are no subnodes!
                if r.random() < 0.5:
                    self.__mutate_value()
                else:
                    self.__mutate_all()

        else:                   #change whole node
            self.__mutate_all()

    def __random_subnode(self):
        """Pick a subnode randomly. Avoid root.
        A node can have two OR one child."""
        if r.random() < 0.5:
            pick = self.__first
        else:
            pick = self.__second
            if pick is None:
                pick = self.__first

        if pick is None:
            return self

        while r.random() < 0.667:
            # go deeper
            left = (r.random() < 0.5)
            if (left and pick.__first) or (not left and pick.__second):
                pick = pick.__first if left else pick.__second
            else:
                break
        return pick

    def copulate(self, partner):
        node1 = self.__random_subnode().clone()
        node2 = partner.__random_subnode().clone()
        node1.swap(node2)
        return [node1, node2]

    @staticmethod
    def random_node(level, max_level=50):
        """Generate random tree"""
        _operators = legal_two
        _leaves = ['x', 'e',  'pi']
        _leaves.extend(['x'] * 10) #just to make sure it get picked
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
