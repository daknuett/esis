import os
import pathlib
import json

import gpt as g
g.default.set_verbose("io", False)

import numpy as np

from lattice_data_db.htp_db.datastore import HTPStore

import sqlite3 

taskid = int(os.environ["SLURM_ARRAY_TASK_ID"])
with open(f"parameters/parameters.{taksid}.json", "r") as fin:
    parameters = json.load(fin)

taks = parameters["task"]

fermion_file = parameters["fermion_file"]
with open(fermion_file) as fin:
    fermion_p = json.load(fin)



my_config = parameters["config"]

configno = my_config._relapath.split(".")[0]
maxiter = parameters["training"]["maxiter"]
ntrainvectors = parameters["training"]["ntrainvectors"]


file_name_base = f"{configno}_coarse_lptc1h1l_{ntrainvectors}_{maxiter}_Wscale{task[0]}_alpha{task[1]}"
file_name_cost = "cost_" + file_name_base + ".csv"
file_name_weights = "weights_" + file_name_base

loadpath = os.path.join(parameters["ensemble"], my_config)
U = g.load(loadpath)

grid = U[0].grid
rng = g.random(parameters["seed"])


src = g.vspincolor(grid)
src[:] = g.vspincolor([[1, 1, 1], [1, 1, 1], [1, 1, 1], [1, 1, 1]])

w = g.qcd.fermion.wilson_clover(U, fermion_p)


mg_setup_2lvl_dp = g.load(os.path.join(parameters["path_to_multigrid_setup"], f"multigrid_setup_{configno}"))

coarse_grid = mg_setup_2lvl_dp[0][0]
u_bar = mg_setup_2lvl_dp[0][1]

b = g.block.map(coarse_grid, u_bar)
l = g.ml.layer
restrict = l.block.project(b)
prolong = l.block.promote(b)
l = g.ml.layer

# identies on coarse grid
one = g.complex(coarse_grid)
one[:] = 1

g.message(one.grid)

I = [ g.copy(one) for i in range(4)]
paths = [g.path().forward(i) for i in range(4)] + [g.path().backward(3)]

# coarse - grid vector space
cot_i = g.ot_vector_complex_additive_group(len(u_bar))
cot_w = g.ot_matrix_complex_additive_group(len(u_bar))

lptc = l.local_parallel_transport_convolution
def coarse_lptc(n_in , n_out):
    return lptc(coarse_grid, I, paths, cot_i, cot_w, n_in, n_out)

ptc = l.parallel_transport_convolution
model = g.ml.model.sequence(restrict, coarse_lptc(1, 1), prolong)

w_coarse = b.coarse_operator(w)
src_coarse = b.project(src)

W = model.random_weights(rng)

for weight in W:
    weight *= task[0]

adam_kwargs = parameters["adam_kwargs"]
adam_kwargs.update({"maxiter": maxiter})

opt = g.algorithms.optimize.adam(**adam_kwargs)

costs = []

data_meta = {"adam": adam_kwargs
             , "physics": fermion_p
             , "configno": configno
             , "sampling": "coarse"
             , "Wscale": task[0]
             , "alpha": task[1]
             , "ntrainvectors": ntrainvectors}

data_tag = f"train_coarse_lptc_1h1l_sample_fine_scanning.{configno}.{taskid}"
data_group = f"train_coarse_lptc_1h1l_sample_fine_scanning.{configno}"
def training_step(k):
    source = g.random.normal(rng, src)
    training_outputs = [source]
    training_inputs = [g(w * s) for s in training_outputs] 

    normalizations = [g.norm2(inp) for inp in training_inputs]
    training_inputs = [g(inp / norm**0.5) for inp,norm in zip(training_inputs, normalizations)]
    training_outputs = [g(oup / norm**0.5) for oup,norm in zip(training_outputs, normalizations)]
    
    cost = model.cost(training_inputs, training_outputs)
    if(costs == []):
        costs.append([-1, -1, cost(W)])
    opt(cost)(W, W)


    costvalue = cost(W)
    costs.append([k, k*maxiter, costvalue])
    
    return W



for k in range(ntrainvectors):
    g.message(k)
    training_step(k)


if(g.rank() == 0):
    costs = np.array(costs)
    store = HTPStore.open("coarse_lptc_scanning", abspath=parameters["db_abspath"])
    store.store(data_tag, costs, group=data_group, meta=data_meta)
    g.message(store._full_path)
    g.message(f"saved {data_tag}")
g.message("done")
