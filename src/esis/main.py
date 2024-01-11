#!/usr/bin/env python3

"""
================================================================================
#                    ESIS2 -- Easy SLURM Isolated Scanner                      #
#                    ------------------------------------                      #
================================================================================

Sets up slurm-based workflows and submits them. Run `esis --help` or `esis doc`
for information.

Usage: 
    esis --help 
    esis doc
    esis setup <setupscript> <sbatchtemplate> <workerscript> <param_generator> [<parameter_include> ...] [options]
    esis run [<workflowfile>]
    esis require <requirementworkflowfile> <requirementname> [<workflowfile>] [--workflow-out]
    esis dependency [<workflowfile>]
    esis list [<list-path>] [options]
    esis list-requirements [<workflowfile>]
    esis freeze-requirement <requirementname> <requirementhash> [<workflowfile>] [--workflow-out]

Global Options:
    -h --help                                   display this help message

Setup Options:
    -o --workflow-out=<workflowfileout>         set the used workflow file [default: ./wf.esis2.json]
    -m --max-parallel=<maxparallel>             maximum number of parallel slurm array jobs [default: 10]
    --workdir-path=<workdir-path>               directory in which workdirs will be created [default: none]

List Options:
    --by-time                                   List by workflow start time.
    --by-jobid                                  List by workflow jobid.
    --grep                                      Output as single lines that can be used in combination with grep.

When both `--by-time` and `--by-jobid` are specified, sorting is done by time.
"""

import docopt
import datetime
import os
import json
import sys
import hashlib
import shutil
import subprocess

from .cmd.const import doc
from .cmd.setup import setup_wf, add_requirement
from .cmd.status import (get_wf_status
                     , get_wf_status_file_content
                     , get_workdir_name
                     , get_workdir
                     , get_wf_run_exits)
from .cmd.run import run, run_workflow
from .cmd.dependency import dependency_run
from .cmd.list_workdirs import list_workdirs
from .cmd.requirements import list_requirements, freeze_requirement

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
        
    if(args["list"]):
        list_workdirs(args)

    if(args["list-requirements"]):
        list_requirements(args)

    if args["freeze-requirement"]:
        freeze_requirement(args)


    print("+------------------------------------------------------------------------------+")
    print("|                            finalized ESIS2                                   |")
    print("+------------------------------------------------------------------------------+")

if __name__ == "__main__":
    main()
