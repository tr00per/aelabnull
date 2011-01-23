#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import numpy as np
import math
import random as r
import getopt as go

import matplotlib.pyplot as plt
import tokenize as tok
from StringIO import StringIO

remaining_tokens = []
open_parenthesis = 0

oper_probability = 1.0

#legal_one_filter = ("__doc__", "__name__", "__package__", "atan2", "copysign", "e", "fmod", "frexp", "fsum", "hypot", "isinf", "isnan", "ldexp", "modf", "pi", "pow")
#legal_one = tuple( [elem for elem in dir(math) if elem not in legal_one_filter] )
legal_one = ('acos', 'acosh', 'asin', 'asinh', 'atan', 'atanh', 'cos', 'cosh', 'exp', 'log', 'log10', 'sin', 'sinh', 'sqrt', 'tan', 'tanh')
legal_two = ('+', '-', '*', '/', '//', '**')
legal_op = legal_two + legal_one
legal_other = ("x", "e", "pi")
legal_all = legal_other + legal_op

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
        Two-argument operators: +, -, *, /, //, %, **
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

                try:
                    right = str(self.__second.calc(x))
                except ZeroDivisionError:
                    right = "np.inf" #depends on numpy as np module import!

                try:
                    return str(eval(left + self.__value + right))
                except ValueError, OverflowError:
                    raise ZeroDivisionError

            elif self.__value in legal_one:
                if self.__second is not None:
                    raise ChildException("too many children for operator " + self.__value)
                try:
                    arg = str(self.__first.calc(x))
                except ZeroDivisionError:
                    arg = "np.inf" #depends on numpy as np module import!

                try:
                    return str(eval("math." + self.__value + "(" + arg + ")" )) #depends on math module import!
                except ValueError, OverflowError:
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

    @staticmethod
    def random_node(level, max_level=100):
        """Generate random tree"""
        _operators = legal_two
        _leaves = ['x', 'e', 'x', 'pi', 'x']
        _leaves.extend(np.arange(-10, 10, 0.5))
        _functions = legal_one

        _oper_probability = oper_probability / (level+1.0); # the deeper, the more leaves
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

class Population:
    def __init__(self, n, maxEpoch, x_from, x_to, target):
        self.MAXEPOCH = maxEpoch
        self.FROM = x_from
        self.TO = x_to
        self.STEP = np.abs(x_to - x_from) * 0.05 #21 control points
        self.TARGET = self.__calc_values(target)

        self.POP = [self.random_individual() for i in range(n)]
        print self.POP[0]

    def __calc_values(self, target):
        ret = []
        for x in np.arange(self.FROM, self.TO+self.STEP, self.STEP):
            try:
                ret.append(target.calc(x))
            except ZeroDivisionError:
                ret.append(np.inf)
        return np.array(ret)

    def random_individual(self):
        return Node.random_node(0)


def parse_recursion():
    global remaining_tokens, open_parenthesis

    toknum, token = remaining_tokens.pop(0) # get first
    get_next = True
    needs_children = False # who does...

    while get_next and toknum != 0:
        #REMOVE_ME print remaining_tokens
        get_next = False # default
        if toknum == 51:
            if token == '(':
                open_parenthesis += 1
                get_next = True
            elif token == ')':
                open_parenthesis -= 1
                get_next = True
                if open_parenthesis < 0:
                    print "Parsing error, parenthesis mismatch (too many closed ones)"
                    exit(1)
            if get_next:
                #REMOVE_ME print "Ignoring token %s, fetching..." % token
                toknum, token = remaining_tokens.pop(0) # get again\
                #REMOVE_ME print "got %s" % token
            else:
                needs_children = True

    #REMOVE_ME print "parsing token %s" % token
    if toknum == 1:
        if token not in legal_other:
            needs_children = True # will be an operator or function
    elif toknum == 0:
        # this should happen only during the second "cleanup parenthesis" call
        return None

    node = Node(token)
    is_math = token in dir(math) # operators have two children. usually.

    #REMOVE_ME print "Operator %s needs %d childen." % (token, (0 if not needs_children else (1 if is_math else 2)))
    if needs_children:
        #REMOVE_ME print "first child..."
        node.addChild(parse_recursion()) # first child
        if not is_math:
            #REMOVE_ME print "second child..."
            node.addChild(parse_recursion()) # second child

    return node

def parse(function):
    """Gets input string (in Polish notation) and returns root of tree of Nodes"""
    global remaining_tokens, open_parenthesis
    if function == "demo":
        root =  Node("**")
        root.addChild(Node("3"))
        sub = Node("+")
        root.addChild(sub)
        sub.addChild(Node("1"))
        sub.addChild(Node("x"))
        return root

    tokens = tok.generate_tokens(StringIO(function).readline)
    try:
        for toknum, tokval, _, _, _ in tokens: #1 - symbol (np. sin), 2 - liczba, 51 - operator albo (), 0 - koniec
            remaining_tokens.append((toknum, tokval))

    except tok.TokenError as e:
        #print "Parsing error: ", str(e)
        return None

    # cool, no errors. now, seriously, parse.
    root = parse_recursion() # this should build up the tree
    none = parse_recursion() # this should return nothing, since only parenthesis should follow
    if open_parenthesis != 0 or none != None:
        #print none
        print "Parsing error, parenthesis mismatch (%d left open after parsing)" % open_parenthesis
        exit(1)

    return root

if __name__ == "__main__":
    inputExpr = "demo"
    x_from = -2.0
    x_to = 2.0
    n = 20
    maxEpoch = 100

    opts, args = go.getopt(sys.argv[1:], "i:f:t:n:n:o:")
    for opt, arg in opts:
        if opt == "-i":
            inputExpr = arg
        if opt == "-f":
            x_from = float(arg)
        if opt == "-t":
            x_to = float(arg)
        if opt == "-n":
            n = int(arg)
        if opt == "-m":
            maxEpoch = int(arg)
        if opt == "-o":
            oper_probability = float(arg)

    target = parse(inputExpr)
    print "Seeking antiderivative for ' %s '!" % target

    pop = Population(n, maxEpoch, x_from, x_to, target)

    if target is not None:
        print "Test case:"
        print target.calc(1)
        print pop.POP[0].calc(-2),
        print pop.POP[0].calc(-1),
        print pop.POP[0].calc(0),
        print pop.POP[0].calc(1),
        print pop.POP[0].calc(2)
        print target
