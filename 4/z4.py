#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import numpy as np
import math as m
import random as r
import getopt as go

import matplotlib.pylot as plt

if __name__ == "__main__":
    demoMode = False;

    opts, args = go.getopt(sys.argv[1:], "D")
    for opt, arg in opts:
        if opt == "-D":
            demoMode = True

    print "Hello world!"
