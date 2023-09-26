#!/usr/bin/env python3

"""
================================================================================
#                    ESIS2 -- Easy SLURM Isolated Scanner                      #
#                    ------------------------------------                      #
================================================================================

Sets up slurm-based workflows and submits them. Run `esis2 --help` or `esis2 doc`
for information.

Usage: 
    esis2 --help 
    esis2 doc
    esis2 setup <setupscript> <sbatchtemplate> <workerscript> <param_generator> [<parameter_include> ...] [options]
    esis2 run [<workflowfile>] [options]
    esis2 require <requirementworkflowfile> <requirementname> [<workflowfile>]
    esis2 dependency [<workflowfile>]

Options:
    -h --help                                   display this help message
    -o --workflow-out=<workflowfileout>         set the used workflow file [default: ./wf.esis2.json]
    -m --max-parallel=<maxparallel>             maximum number of parallel slurm array jobs [default: 10]
    --workdir-path=<workdir-path>               directory in which workdirs will be created [default: none]

"""

import docopt
import datetime
import os
import json
import sys
import hashlib
import shutil
import subprocess

from .const import doc
from .setup import setup_wf, add_requirement
from .status import (get_wf_status
                     , get_wf_status_file_content
                     , get_workdir_name
                     , get_workdir
                     , get_wf_run_exits)
from .run import run, run_workflow
from .dependency import dependency_run

def main():
    args = docopt.docopt(__doc__)
    print("================================================================================")
    print("#                   ESIS2 -- Easy SLURM Isolated Scanner 2                     #")
    print("#                   --------------------------------------                     #")
    print("================================================================================")

    if(args["setup"]):
        setup_wf(args)
    if(args["require"]):
        add_requirement(args)
    if(args["run"]):
        run(args)
    if(args["doc"]):
        print(doc)
    if(args["dependency"]):
        dependency_run(args)
        


    print("+------------------------------------------------------------------------------+")
    print("|                            finalized ESIS2                                   |")
    print("+------------------------------------------------------------------------------+")

if __name__ == "__main__":
    main()
