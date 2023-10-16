import numpy as np
import os
import json

import esis


taskid = int(os.environ["SLURM_ARRAY_TASK_ID"])

with open(f"../parameters/parameters.{taskid}.json", "r") as fin:
    parameters = json.load(fin)

load_chkpts = esis.checkpoint.checkpoint_facility.open_external(parameters["trained_weights"])


checkpoint = load_chkpts.load_checkpoint(f"final_{parameters['weight_id']}")
W = np.load(checkpoint.get_file_name("weights.npy"))

one = np.zeros_like(W)
dg = np.diag(one)
one += np.diag(np.ones_like(dg))

error = np.sum((W - one)**2)

np.savetxt(f"error.{parameters['weight_id']}.csv", error)
    
