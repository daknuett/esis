import numpy as np
import os
import json

import esis

"""
This file illustrates the learning of a simple 
matrix operator. We want to learn $O = I$.

Furthermore, it shows how esis can be used for checkpointing.
"""

class Layer:
    def __init__(self, nin, nout):
        self._nin = nin
        self._nout = nout
        #self._weights = self.random_weights()
        
    def random_weights(self):
        return np.random.uniform(-1, 1, (nout, nin))
    
    def call(self, W, vin):
        return W @ vin
    
    def dcall(self, W, vin):
        dW = np.zeros_like(W)
        y = self.call(W, vin)
        for k in range(vin.shape[0]):
            dW[:,k] = y
        for i in range(y.shape[0]):
            dW[i,:] *= vin
        return dW
    
    def darg(self, W, vin):
        return W

class Model:
    def __init__(self, layer: Layer):
        self._layer = layer
        
    def cost(self, W, vin, b):
        return np.linalg.norm(self._layer.call(W, vin) - b)**2
    
    def dcost(self, W, vin, b):
        dW = self._layer.dcall(W, vin)
        bterm = np.zeros_like(dW)
        for k in range(vin.shape[0]):
            bterm[:,k] -= b
        for i in range(b.shape[0]):
            bterm[i,:] *= vin
            
        return 2*(dW - bterm)

def gd(model, Winit, vin, b, eps=1e-5, alpha=1e-3, maxiter=1000):
    W = np.copy(Winit)
    
    for k in range(maxiter):
        dW = model.dcost(W, vin, b)
        if(np.sum(dW**2) < eps):
            return W, (True, k)
        
        costold = model.cost(W, vin, b)
        W -= alpha*dW
        costnew = model.cost(W, vin, b)
        
        #print(costold, "->", costnew)
        
    
    return W, (False, k)


taskid = int(os.environ["SLURM_ARRAY_TASK_ID"])

with open(f"../parameters/parameters.{taskid}.json", "r") as fin:
    parameters = json.load(fin)


np.random.seed(parameters["baseseed"])

nin = parameters["nin"]
nout = parameters["nout"]

l = Layer(nin, nout)
W = l.random_weights()
model = Model(l)

nepochs = parameters["nepochs"]

chkpts = esis.checkpoint.checkpoint_facility(parameters["baseseed"])    
save_every = 10
save_name = "weights.npy"    
training_checkpoint_name = f"weight_training_{taskid}"
     
if(chkpts.has_iterative_checkpoint(training_checkpoint_name)):    
    checkpoint = chkpts.open_iterative(training_checkpoint_name)
else:
    checkpoint = chkpts.create_iterative_checkpoint(training_checkpoint_name)

np.random.seed(checkpoint.get_seed_int())

for step in range(checkpoint.get_iteration(), nepochs, save_every):    
    for k in range(step, step + save_every):
        x = np.random.uniform(0, 1, nin)
        W, (conv, iters) = gd(model, W, x, x, maxiter=parameters["maxiter"], alpha=parameters["alpha"])
    np.save(checkpoint.get_file_name(save_name), W)    
    checkpoint.set_iteration(step + save_every)
    np.random.seed(checkpoint.get_seed_int())

if(not chkpts.has_checkpoint(f"final_{taskid}")):
    checkpoint = chkpts.create_checkpoint(f"final_{taskid}")
    np.save(checkpoint.get_file_name(save_name), W)    
    checkpoint.set_OK()    

chkpts.set_run_OK()
