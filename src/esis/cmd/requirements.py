#!/usr/bin/env python3
import os
import json
import sys

from collections import defaultdict

from .status import get_workdir_name, get_workdir, get_wf_run_exits, get_wf_status_file_content

def list_requirements(arguments):
    wf_in_name = arguments["<workflowfile>"]
    if(wf_in_name is None):
        wf_in_name = arguments["--workflow-out"]

    if(not os.path.exists(wf_in_name)):
        print("===> FATAL: missing input workflow:", wf_in_name)
        sys.exit(1)

    wf_path = os.path.dirname(os.path.abspath(wf_in_name))
    with open(wf_in_name, "r") as fin:
        workflow = json.load(fin)

    
    freezes = defaultdict(type(None))
    if "freeze_requirements" in workflow:
        freezes.update(workflow["freezes"])
    
    missing_requirements = set(req for req in workflow["requires"] if not get_wf_run_exits(req, parent_wfpath=wf_path, freeze=freezes[req]))
    requirement_dirs = {req_wf: get_workdir(req_wf, parent_wfpath=wf_path, freeze=freezes[req_wf]) for req_wf in workflow["requires"]}
    existing_requires = {req_wf: os.path.exists(pth)  for req_wf, pth in requirement_dirs.items()}

    def isfixed(val):
        return val is not None
    fixed = {req_wf: isfixed(freezes[req_wf]) for req_wf in workflow["requires"]}


    output = [(workflow["requires_names"][req], req, requirement_dirs[req], existing_requires[req], fixed[req]) for req in  sorted(workflow["requires"])]

    if sys.stdout.isatty():
        fancy_prefix_e = {True: "\033[92m", False: "\033[91m"}
        fancy_prefix_f = {True: "\033[4m", False: ""}
        fancy_postfix = "\033[0m"
    else:
        fancy_prefix_e = {True: "", False: ""}
        fancy_prefix_f = {True: "", False: ""}
        fancy_postfix = ""

    label_exists = {True: "y", False: "n"}
    label_fixed = {True: "Y", False: "N"}

    output_lengths = [max(map(len, out)) for out in output[:-2]]
    def getpad2(string, lenp):
        return string + (" " * (lenp - len(str)))

    for reqname, req, reqdir, reqexist, reqfixed in output:
        print(fancy_prefix_e[reqexist], end="")
        print(fancy_prefix_f[reqfixed], end="")
        print(getpad2(reqname, output_lengths[0] + 2), end="")
        print(getpad2(req, output_lengths[1] + 2), end="")
        print(getpad2(reqdir, output_lengths[2] + 2), end="")
        print(label_exists[reqexist] + " ", end="")
        print(label_fixed[reqfixed] + " ", end="")
        print(fancy_postfix)

