#!/usr/bin/env python3
import json

alphas = [1e-2, 1e-3]

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
