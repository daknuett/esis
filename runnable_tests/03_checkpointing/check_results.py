import sys
import numpy as np
import esis
import os


chkpts = esis.checkpoint.checkpoint_facility("")

for taskid in [0, 1]:
    if(not chkpts.has_checkpoint(f"final_{taskid}")):
        sys.exit(1)
    checkpoint = chkpts.load_checkpoint(f"final_{taskid}")
    try:
        np.load(checkpoint.get_file_name("weights.npy"))
    except:
        sys.exit(1)

    # TODO: check for W \approx I
