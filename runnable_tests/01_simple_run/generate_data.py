#!/usr/bin/env python3

import os
import sys
import numpy as np


"""
This script generates phony path configurations.
"""

if(len(sys.argv) != 3):
    print("ERROR: arguments must be mass:float, outpath:str")
    sys.exit(1)

try:
    mass = float(sys.argv[1])
except:
    print("ERROR: arguments must be mass:float, outpath:str")
    sys.exit(1)


nt = 10
nconfigs = 100_000

omega = 1 
var = 1 / (2. * omega * mass)

data = np.random.normal(loc=0, scale=np.sqrt(var), size=(nt, nconfigs))

np.save(sys.argv[2], data)
