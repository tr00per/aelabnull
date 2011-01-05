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
        """Operators are things that are not floats. Validatet later
        Two-argument operators: +, -, *, /, //, %, **
        One-argument operators: sin, cos, tan, sqrt and so on (math module)
        Actual list is held in Node::calc()
        """
        self.__operator = False
        self.__first = None
        self.__second = None

        self.__value = str(value).strip()

        try:
            testVar = float(self.__value)
        except ValueError:
            self.__operator = True

    def addChild(self, child):
        if self.__first is None:
            self.__first = child
            return

        if self.__second is None:
            self.__second = child
            return

        raise ChildException("child addition")

    def calc(self):
        if self.__operator:
            if self.__first is None: #has at least one child?
                raise ChildException("none children given for operator " + self.__value)

            if self.__value in ('+', '-', '*', '/', '//', '%', '**'):
                if self.__second is None:
                    raise ChildException("too few children for operator " + self.__value)
                return str(eval(self.__first.calc() + self.__value + self.__second.calc()))

            elif self.__value in dir(math):
                if self.__second is not None:
                    raise ChildException("too many children for operator " + self.__value)
                return str(eval("math." + self.__value + "(" + self.__first.calc() + ")" )) #depends on math module import!

            else:
                raise OperatorException(self.__operator)

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
        """Generate random tree"""
        pass

def parse(function):
    """Gets input string (in Polish notation) and returns root of tree of Nodes"""
    if function == "demo":
        root =  Node("**")
        root.addChild(Node("3"))
        sub = Node("+")
        root.addChild(sub)
        sub.addChild(Node("1"))
        sub.addChild(Node("1"))
        return root
    print "Nah, not yet."

    tokens = generate_tokens(StringIO(function).readline)

    root = Node("0")
    return root

if __name__ == "__main__":
    inputExpr = "demo"

    opts, args = go.getopt(sys.argv[1:], "i")
    for opt, arg in opts:
        if opt == "-i":
            inputExpr = arg

    print "Growin tree!"

    tree = parse(inputExpr)
    print tree.calc()
    print tree
