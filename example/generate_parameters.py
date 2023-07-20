#!/usr/bin/env python3

import itertools
import json


ensemble = "/glurch/scratch/knd35666/ensembles/ens001"
configs = ["1500.config", "1200.config"]
seed = "0xdeadbeef"

training = {"maxiter": 1, "ntrainvectors": 1000}
adam_kwargs = dict(maxiter=1000, eps=1e-8, beta1=0.9, beta2=0.98, eps_regulator=0.1)

sampling = "coarse"

Wscales_oom = [1e-4, 1e-3, 1e-2, 1e-1, 1e0]
Wscales = [scl * oom for scl in [1, 5] for oom in Wscales_oom]

alphas_oom = [1e-4, 1e-3, 1e-2, 1e-1, 1e0, 1e1]
alphas = [scl * oom for scl in [1, 5] for oom in alphas_oom]

tasks = list(itertools.product(Wscales, alphas))
path_to_multigrid_setup = "../../multigrid_setup"
fermion_file = "../../fermion_parameters.json"
db_abspath = "../"


for i, (c, tsk) in enumerate(itertools.product(configs, tasks)):
    parameters = {
            "ensemble": ensemble
            , "config": c 
            , "training": training
            , "adam_kwargs": adam_kwargs
            , "sampling": sampling
            , "task": tsk
            , "seed": seed
            , "path_to_multigrid_setup": path_to_multigrid_setup
            , "fermion_file": fermion_file
            , "db_abspath": db_abspath
            }
    with open(f"parameters.{i}.json", "w") as fout:
        json.dump(parameters, fout)

print(i)
