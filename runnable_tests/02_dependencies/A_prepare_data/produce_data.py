#!/usr/bin/env python3

import os
import sys
import numpy as np


"""
This script generates phony path configurations.
"""

taskid = int(os.environ["SLURM_ARRAY_TASK_ID"])

with open(f"../parameters/parameters.{taskid}.json", "r") as fin:
    parameters = json.load(fin)

mass = parameters["mass"]
out_path = parameters["out_path"]


nt = 10
nconfigs = 100_000

omega = parameters["omega"] 
var = 1 / (2. * omega * mass)

data = np.random.normal(loc=0, scale=np.sqrt(var), size=(nt, nconfigs))

np.save(out_path, data)

