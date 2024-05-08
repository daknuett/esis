#!/usr/bin/env python3

import os
import json

requirements = json.loads(os.environ["ESIS2_REQUIREMENTS"])

data_path = os.path.join(requirements["data_generation"], "output")
omegas = [1, 2.3, 2.4, 2.5] 

for i,o in enumerate(omegas):
    parameters = {"omega": o
                  , "data_path": data_path
                  , "file": f"data.{i}.npy"
                  , "out_path": f"../output/"
                  }

    with open(f"parameters.{i}.json", "w") as fout:
        json.dump(parameters, fout)

print(i)


