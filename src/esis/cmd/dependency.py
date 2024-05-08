import os
import json
import hashlib
import subprocess

from .status import get_wf_status, get_wf_run_exits
from .run import run_workflow



def get_all_dependencies(wf_file, orig_wf_path, parent_wf_path=None):
    if(parent_wf_path is not None and not os.path.isabs(wf_file)):
        wf_file = os.path.join(parent_wf_path, wf_file)

    with open(wf_file, "r") as fin:
        workflow = json.load(fin)
    wf_path = os.path.dirname(os.path.abspath(wf_file))

    this_wf = os.path.relpath(os.path.abspath(wf_file), orig_wf_path)
    requirements = [os.path.relpath(os.path.join(wf_path, req), orig_wf_path) for req in workflow["requires"]]

    dependencies = {this_wf: {"dependencies": requirements}}
    for req in workflow["requires"]:
        dependencies.update(get_all_dependencies(req, orig_wf_path, parent_wf_path=wf_path))
    return dependencies


def order_workflows(workflows, root):
    for wf in workflows.values():
        wf["weight"] = -1

    workflows[root]["weight"] = 0

    def update_dependency(cweight, dependency):
        if(workflows[dependency]["weight"] >= cweight):
            return
        workflows[dependency]["weight"] = cweight

        for dep in workflows[dependency]["dependencies"]:
            update_dependency(cweight + 1, dep)

    update_dependency(1, root)
    return workflows


def run_workflow_graph(workflows, orig_wf_path):
    # FIXME:
    # At the moment I am not sure if this will work properly with 
    # frozen dependencies. But the worst case is that some unused 
    # runs will be made.
    # Note that in any case, freezing may be incompatible with automatic 
    # running, because there is no way to find what to run for a specific 
    # freeze.
    for wf in workflows:
        workflows[wf]["jobid"] = None

    # First, run all workflows without 
    # dependencies.
    no_deps = [wf for wf, wfd in workflows.items() if len(wfd["dependencies"]) == 0]
    print(f"---> found {len(no_deps)} workflows without dependencies")
    for wf in no_deps:
        workflows[wf]["jobid"] = run_workflow(os.path.join(orig_wf_path, wf))

    weights = [wfd["weight"] for wfd in workflows.values()]

    def run_workflows_at_weight(weight):
        workflows_to_run = [wf for wf, wfd in workflows.items() 
                                if wfd["weight"] == weight and wfd["jobid"] is None]
        print(f"---> found {len(workflows_to_run)} workflows at weight {weight}")
        for wf in workflows_to_run:
            dependencies = [workflows[i]["jobid"] for i in workflows[wf]["dependencies"]]
            workflows[wf]["jobid"] = run_workflow(os.path.join(orig_wf_path, wf), afterok=dependencies)


    cweight = max(weights)
    while(cweight >= 1):
        run_workflows_at_weight(cweight)
        cweight -= 1

def dependency_run(arguments):
        wf_in_name = arguments["<workflowfile>"]
        if(wf_in_name is None):
            wf_in_name = arguments["--workflow-out"]

        wfs = get_all_dependencies(wf_in_name, os.path.dirname(wf_in_name))
        wfs = order_workflows(wfs, os.path.basename(wf_in_name))

        run_workflow_graph(wfs, os.path.dirname(wf_in_name))


