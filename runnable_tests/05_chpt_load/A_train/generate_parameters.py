#!/usr/bin/env python3
import json

with open("../includes/alphas.json") as fin:
    alphas = json.load(fin)

for i,a in enumerate(alphas):
    parameters = {
            "alpha": a
            , "nin": 5
            , "nout": 5
            , "maxiter": 30_000
            , "baseseed": 0xdeadbeef
            , "nepochs": 400
    }
    with open(f"parameters.{i}.json", "w") as fout:
        json.dump(parameters, fout)

print(i)
