#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import getopt as go

import matplotlib.pyplot as plt
import tokenize as tok
from StringIO import StringIO

import math
from consts import *
from node import Node
from population import Population

remaining_tokens = []
open_parenthesis = 0

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
    if open_parenthesis != 0 or none is not None:
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
            #default value at the end od node.py
            Node.oper_probability = float(arg)

    target = parse(inputExpr)
    print "Seeking antiderivative for ' %s '!" % target

    pop = Population(n, x_from, x_to, target)

    if inputExpr != "demo":
        for epoch in range(maxEpoch):
            if epoch % 20 == 0:
                print "Epoch", epoch
            pop.epoch()

        print "Epoch", maxEpoch
        print std(pop.POP[0])

    else:
        print "Test case:"
        print target.calc(1)
        print pop.POP[0]
        print pop.POP[0].calc(-2),
        print pop.POP[0].calc(-1),
        print pop.POP[0].calc(0),
        print pop.POP[0].calc(1),
        print pop.POP[0].calc(2)
        print target
