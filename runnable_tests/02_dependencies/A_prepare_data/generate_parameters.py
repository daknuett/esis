#!/usr/bin/env python3

import json

omegas = [1, 2.3, 2.4, 2.5] 

for i,o in enumerate(omegas):
    parameters = {"omega": 1
                  , "data_path": data_path
                  , "file": f
                  , "out_path": f"../output/data.{i}.npy"
                  }

    with open(f"parameters.{i}.json", "w") as fout:
        json.dump(parameters, fout)

print(i)

