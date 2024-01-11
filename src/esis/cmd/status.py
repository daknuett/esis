import os
import json
import hashlib
import subprocess

from collections import defaultdict

def get_wf_status(workflowfile):
    with open(workflowfile, "r") as fin:
        workflow = json.load(fin)

    wf_path = os.path.dirname(os.path.abspath(workflowfile))
    test_files = ["setupscript", "sbatchtemplate", "workerscript", "param_generator"]
    status = {}
    for tf in test_files:
        with open(os.path.join(wf_path, workflow[tf]), "rb") as fin:
            status[tf] = hashlib.sha256(fin.read()).hexdigest()

    include_status = {}
    for include in workflow["param_includes"]:
        with open(os.path.join(wf_path, include), "rb") as fin:
            include_status[include] = hashlib.sha256(fin.read()).hexdigest()

    status["param_includes"] = include_status

    freezes = defaultdict(type(None))
    if "freeze_requirements" in workflow:
        freezes.update(workflow["freezes"])

    print("requires:", workflow["requires"])
    status["requires"] = [(req, freezes[req]) for req in workflow["requires"]]

    return status

def get_wf_status_file_content(workflowfile):
    status = get_wf_status(workflowfile)
    wf_path = os.path.dirname(os.path.abspath(workflowfile))

    requires = {}
    print("requires:", status["requires"])
    for req, frz in status["requires"]:
        print("req:", req)
        if frz is None:
            if(not os.path.isabs(req)):
                req_path = os.path.join(wf_path, req)
            else:
                req_path = req
            requires[req] = hashlib.sha256(get_wf_status_file_content(req_path).encode("UTF-8")).hexdigest()
        else:
            requires[req] = frz

    test_files = ["setupscript", "sbatchtemplate", "workerscript", "param_generator"]
    include_names = list(sorted(status["param_includes"].keys()))
    requires_names = list(sorted(status["requires"]))
    print("req_names:", requires_names)

    all_tags = test_files + include_names + requires_names 
    all_content = {tf: status[tf] for tf in test_files}
    all_content.update(status["param_includes"])
    all_content.update(requires)

    return "\n".join(":".join((k, all_content[k])) for k in all_tags)

def get_workdir_name(workflowfile):
    wf_status = hashlib.sha256(get_wf_status_file_content(workflowfile).encode("UTF-8")).hexdigest()
    return f"wrkdir.{wf_status}"


def get_workdir(workflowfile, parent_wfpath=None, freeze=None):
    if(not (parent_wfpath is None or os.path.isabs(workflowfile))):
        workflowfile = os.path.join(parent_wfpath, workflowfile)
    if freeze is None:
        workdirname = get_workdir_name(workflowfile)
    else:
        workdirname = f"wrkdir.{freeze}"

    with open(workflowfile, "r") as fin:
        workflow = json.load(fin)

    wf_path = os.path.dirname(os.path.abspath(workflowfile))

    if(os.path.isabs(workflow["workdirpath"])):
        full_workdir = os.path.join(workflow["workdirpath"], workdirname)
    else:
        full_workdir = os.path.join(wf_path, workflow["workdirpath"], workdirname)

    return full_workdir


def get_wf_run_exits(workflowfile, parent_wfpath=None, freeze=None):
    """
    Returns 0, if the run does not exist.
    Returns 1, if the run directory exists, but it is uncertain, if the 
                workflow completed.
    Returns 2, if the workflow completed.
    """
    if(parent_wfpath is None or os.path.isabs(workflowfile)):
        wff = workflowfile
    else:
        wff = os.path.join(parent_wfpath, workflowfile)

    if freeze is None:
        wd = get_workdir(wff)
    else:
        # FIXME: this machinery is very unelegant.
        wd = get_workdir(wff)
        wdroot = os.path.pardir(wd)
        wd = os.path.join(wdroot, f"wrkdir.{freeze}")
        
    if not os.path.exists(wd):
        return 0
    if(not os.path.exists(os.path.join(wd, "__esis__", "completed.state"))):
        return 1
    return 2
