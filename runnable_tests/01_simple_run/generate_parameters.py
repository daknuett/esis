#!/usr/bin/env python3

import json

omega = 1 

data_path = "../../data"
out_path = "../output"
files = ["data-0.npy"
         , "data-1.npy" 
         , "data-2.npy" 
         , "data-3.npy" 
         ]

for i,f in enumerate(files):
    parameters = {"omega": 1
                  , "data_path": data_path
                  , "file": f
                  , "out_path": out_path
                  }

    with open(f"parameters.{i}.json", "w") as fout:
        json.dump(parameters, fout)

print(i)

