import datetime
import os
import json
import sys
import hashlib
import shutil
import subprocess

from .const import dt_format_hr, df_format_m

def setup_wf(arguments):
    wf_out_name = arguments["--workflow-out"]
    maxparallel = arguments["--max-parallel"]
    
    if(arguments["--workdir-path"] == "none"):
        workdirpath = "./"
    else:
        workdirpath = arguments["--workdir-path"]
    
    if(not os.path.isabs(workdirpath)):
        workdirpath = os.path.relpath(workdirpath, os.path.dirname(os.path.abspath(wf_out_name)))

    wf_path = os.path.dirname(os.path.abspath(wf_out_name))


    workflow = {
            "setupscript": arguments["<setupscript>"]
            , "sbatchtemplate": arguments["<sbatchtemplate>"]
            , "workerscript": arguments["<workerscript>"]
            , "param_generator": arguments["<param_generator>"]
            , "param_includes": arguments["<parameter_include>"]
            , "status": {}
            , "requires": []
            , "maxparallel": maxparallel
            , "workdirpath": workdirpath
            , "requires_names": {}
    }

    # Check for presence and +x of files.
    test_files = ["setupscript", "sbatchtemplate", "workerscript", "param_generator"]
    for tf in test_files:
        if(not os.path.exists(workflow[tf])):
            print("===> FATAL: missing file:", workflow[tf])
            sys.exit(1)
        workflow[tf] = os.path.relpath(workflow[tf], wf_path)

    includes_rela = []
    for tf in workflow["param_includes"]:
        if(not os.path.exists(tf)):
            print("===> FATAL: missing file:", tf)
            sys.exit(1)
        includes_rela.append(os.path.relpath(tf, wf_path))
    workflow["param_includes"] = includes_rela

    executable_files = ["setupscript", "param_generator"]
    for tf in executable_files:
        if(not os.access(workflow[tf], os.X_OK)):
            print("===> FATAL: file not executable:", workflow[tf])
            sys.exit(1)

    with open(wf_out_name, "w") as out:
        json.dump(workflow, out)

    print("---> wrote workflow file", wf_out_name)


def add_requirement(arguments):
    wf_in_name = arguments["<workflowfile>"]
    if(wf_in_name is None):
        wf_in_name = arguments["--workflow-out"]

    if(not os.path.exists(wf_in_name)):
        print("===> FATAL: missing input workflow:", wf_in_name)
        sys.exit(1)

    wf_require_name = arguments["<requirementworkflowfile>"]
    if(not os.path.exists(wf_require_name)):
        print("===> FATAL: missing reqired workflow:", wf_in_name)
        sys.exit(1)

    wf_path = os.path.dirname(os.path.abspath(wf_in_name))
    wf_require_rela = os.path.relpath(wf_require_name, wf_path)
    print("---> found relative workflow requirement:", wf_require_rela)

    with open(wf_in_name, "r") as fin:
        workflow = json.load(fin)

    if(wf_require_rela in workflow["requires"]):
        print("===> ERROR: requirement already in workflow:", wf_require_rela)
        sys.exit(1)

    workflow["requires"].append(wf_require_rela)
    workflow["requires_names"][wf_require_rela] = arguments["<requirementname>"]

            
    with open(wf_in_name, "w") as out:
        json.dump(workflow, out)

    print("---> wrote workflow file", wf_in_name)
