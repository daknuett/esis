#!/usr/bin/env python3

import json
import os
import numpy as np


taskid = int(os.environ["SLURM_ARRAY_TASK_ID"])

with open(f"../parameters/parameters.{taskid}.json", "r") as fin:
    parameters = json.load(fin)


data = np.load(os.path.join(parameters["data_path"], parameters["file"]))
omega = parameters["omega"]

var = np.var(data[0,:])

# var = 1/(2*m*omega)
m = 1 / (var * 2 * omega)

np.save(os.path.join(parameters["out_path"], f"mass.{taskid}.npy"), np.array(m))

