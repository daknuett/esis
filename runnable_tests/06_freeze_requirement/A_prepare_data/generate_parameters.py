#!/usr/bin/env python3

import json

omegas = [1, 2.3, 2.4, 2.5] 
masses = [1.2, 1.2, 2.2, 2.2]

for i, (o,m) in enumerate(zip(omegas, masses)):
    parameters = {"omega": o
                  , "mass": m
                  , "out_path": f"../output/data.{i}.npy"
                  }

    with open(f"parameters.{i}.json", "w") as fout:
        json.dump(parameters, fout)

print(i)

