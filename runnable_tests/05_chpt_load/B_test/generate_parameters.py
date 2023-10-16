#!/usr/bin/env python3
import json
import os

with open("../includes/alphas.json") as fin:
    alphas = json.load(fin)

requirements = json.loads(os.environ["ESIS2_REQUIREMENTS"])
trained_weight_path = requirements["trained_weights"]

for i,a in enumerate(alphas):
    parameters = {
            "alpha": a
            , "nin": 5
            , "nout": 5
            , "baseseed": 0xdeadbeef
            , "weight_id": i # This is just the slurm task id, does not really matter.
            , "trained_weights": trained_weight_path
    }
    with open(f"parameters.{i}.json", "w") as fout:
        json.dump(parameters, fout)

print(i)
