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
        self.__allowed_operators = ('+', '-', '*', '/', '**')
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

            if self.__value in self.__allowed_operators:
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

def parse_recursion():
    global remaining_tokens, open_parenthesis

    toknum, token = remaining_tokens.pop(0) # get first
    get_next = True
    needs_children = False # who does...

    while get_next and toknum != 0:
        #print remaining_tokens
        get_next = False # default
        if toknum == 51:
            if token == '(':
                open_parenthesis += 1
                get_next = True
            elif token == ')':
                open_parenthesis -= 1
                get_next = True
                if open_parenthesis < 0:
                    print "Parsing error, parenthesis mismatch"
                    exit(1)
            if get_next:
                print "Ignoring token %s, fetching..." % token
                toknum, token = remaining_tokens.pop(0) # get again\
                print "got %s" % token
            else:
                needs_children = True

    print "parsing token %s" % token
    if toknum == 1:
        needs_children = True # will be an operator or function

    node = Node(token)
    is_math = token in dir(math) # operators have two children. usually.

    print "Operator %s needs %d childen." % (token, (0 if not needs_children else (1 if is_math else 2)))
    if needs_children:
        print "first child..."
        node.addChild(parse_recursion()) # first child
        if not is_math:
            print "second child..."
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
        sub.addChild(Node("1"))
        return root

    tokens = tok.generate_tokens(StringIO(function).readline)
    try:
        for toknum, tokval, _, _, _ in tokens: #1 - symbol (np. sin), 2 - liczba, 51 - operator albo (), 0 - koniec
            sys.stdout.write(tokval+" ") # javish
            remaining_tokens.append((toknum, tokval))

    except tok.TokenError as e:
        print "Parsing error: ", str(e)
        return None

    # cool, no errors. now, seriously, parse.
    root = parse_recursion()
    if open_parenthesis != 0:
        print "Parsing error, parenthesis mismatch (%d left open after parsing)" % open_parenthesis
        exit(1)

    return root

if __name__ == "__main__":
    inputExpr = "demo"

    opts, args = go.getopt(sys.argv[1:], "i:")
    for opt, arg in opts:
        if opt == "-i":
            inputExpr = arg

    print "Growin tree!"

    tree = parse(inputExpr)
    if tree is not None:
        print tree.calc()
        print tree
