import os
import json
import hashlib
import subprocess
import re

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
    status["requires"] = workflow["requires"]

    return status

def get_wf_status_file_content(workflowfile):
    status = get_wf_status(workflowfile)
    wf_path = os.path.dirname(os.path.abspath(workflowfile))

    requires = {}
    for req in status["requires"]:
        if(not os.path.isabs(req)):
            req_path = os.path.join(wf_path, req)
        else:
            req_path = req
        requires[req] = hashlib.sha256(get_wf_status_file_content(req_path).encode("UTF-8")).hexdigest()

    test_files = ["setupscript", "sbatchtemplate", "workerscript", "param_generator"]
    include_names = list(sorted(status["param_includes"].keys()))
    requires_names = list(sorted(status["requires"]))

    all_tags = test_files + include_names + requires_names 
    all_content = {tf: status[tf] for tf in test_files}
    all_content.update(status["param_includes"])
    all_content.update(requires)

    return "\n".join(":".join((k, all_content[k])) for k in all_tags)

def get_workdir_name(workflowfile):
    wf_status = hashlib.sha256(get_wf_status_file_content(workflowfile).encode("UTF-8")).hexdigest()
    return f"wrkdir.{wf_status}"


def get_workdir(workflowfile, parent_wfpath=None):
    if(not (parent_wfpath is None or os.path.isabs(workflowfile))):
        workflowfile = os.path.join(parent_wfpath, workflowfile)
    workdirname = get_workdir_name(workflowfile)

    with open(workflowfile, "r") as fin:
        workflow = json.load(fin)

    wf_path = os.path.dirname(os.path.abspath(workflowfile))

    if(os.path.isabs(workflow["workdirpath"])):
        full_workdir = os.path.join(workflow["workdirpath"], workdirname)
    else:
        full_workdir = os.path.join(wf_path, workflow["workdirpath"], workdirname)

    return full_workdir


def get_wf_run_exits(workflowfile, parent_wfpath=None):
    """
    Returns 0, if the run does not exist.
    Returns 1, if the run directory exists, but it is uncertain, if the 
                workflow completed. (run was invoked by old version of esis).
    Returns 2, if the workflow completed.
    Returns 3, if the workflow did not complete.
    Returns 4, if the workflow is still running.
    """
    if(parent_wfpath is None or os.path.isabs(workflowfile)):
        wff = workflowfile
    else:
        wff = os.path.join(parent_wfpath, workflowfile)
    wd = get_workdir(wff)
    if not os.path.exists(wd):
        return 0
    if(not os.path.exists(os.path.join(wd, "__esis__"))):
        return 1
    if(not os.path.exists(os.path.join(wd, "__esis__", "completed.state"))):
        if not os.path.exists(os.path.join(wd, "__esis__", "jobid.tx")):
            return 1
        with open(os.path.join(wd, "__esis__", "jobid.tx")) as fin:
            jobid = fin.read().strip()

            process = subprocess.run(["scontrol", "show", "job", jobid]
                                     , stdout=subprocess.PIPE
                                     , stderr=subprocess.PIPE)
            if(process.returncode != 0):
                return 1
            jobstate = process.stdout.decode("UTF-8")
            if("JobState=PENDING" in jobstate
               or "JobState=RUNNING" in jobstate):
                return 4
            return 3
            
    return 2
