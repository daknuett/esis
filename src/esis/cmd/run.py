import datetime
import os
import json
import sys
import hashlib
import shutil
import subprocess

from .status import get_workdir_name, get_workdir, get_wf_run_exits, get_wf_status_file_content
from .const import dt_format_hr, df_format_m

def re_run(workdirname):


def run_workflow(wf_in_name, afterok=[], independency=False):
    if(not os.path.exists(wf_in_name)):
        print("===> FATAL: missing input workflow:", wf_in_name)
        sys.exit(1)

    workdirname = get_workdir_name(wf_in_name)
    run_exists = get_wf_run_exits(wf_in_name)
    if(run_exists == 2  or run_exists == 4):
        if(not independency):
            print("###> STATUS: workdir already exists:", workdirname)
            print("###> to re-run, rotate the workdir")
            if(run_exists == 4):
                print("###> WARNING: job still running")
            sys.exit(0)
        with open(os.path.join(get_workdir, wf_in_name), "__esis__", "jobid.tx") as fin:
            return fin.read()
    elif(run_exists == 1):
        print("###> STATUS: workdir already exists:", workdirname)
        print("###> to re-run, rotate the workdir")
        sys.exit(0)
    elif(run_exists == 3):
        print("###> STATUS: workflow did not complete. Re-running.")
        return re_run(workdirname)


    with open(wf_in_name, "r") as fin:
        workflow = json.load(fin)
    full_workdir = get_workdir(wf_in_name)
    wf_path = os.path.dirname(os.path.abspath(wf_in_name))


    missing_requirements = [req  for req in workflow["requires"] if not get_wf_run_exits(req, parent_wfpath=wf_path)]
    if(len(missing_requirements)):
        print("<### STATUS: MISSING REQUIREMENTS")
        print("<### The following requirements have pending changes:")
        for req in missing_requirements:
            print("<---", req)
            print("<--- missing:", get_workdir_name(req))
        print("<### Automatic requirement running is currently not supported.")
        print("<### Run the workflows manually.")
        sys.exit(1)

    now = datetime.datetime.now()
    print("---> INFO: now:", now.strftime(dt_format_hr))

    os.makedirs(full_workdir)


    subdirs = ["cwd", "parameters", "includes", "__esis__"]
    for subdir in subdirs:
        os.makedirs(os.path.join(full_workdir, subdir))

    print("---> created directories")
    print("---> workdir:", full_workdir)

    esis_private_dir = os.path.join(full_workdir, "__esis__")

    with open(os.path.join(esis_private_dir, "wf_status"), "w") as fout:
        fout.write(get_wf_status_file_content(wf_in_name))
    with open(os.path.join(esis_private_dir, "wf_starttime"), "w") as fout:
        fout.write(now.strftime(dt_format_hr))

    workflow_dir = os.path.dirname(os.path.abspath(wf_in_name))

    copy_files = ["setupscript", "workerscript", "param_generator"] 
    for cf in copy_files:
        shutil.copy(os.path.join(workflow_dir, workflow[cf])
                    , os.path.join(full_workdir, workflow[cf]))

    for incl in workflow["param_includes"]:
        try:
            shutil.copy(os.path.join(workflow_dir, incl), os.path.join(full_workdir, "includes", os.path.basename(incl)))
        except Exception as e:
            print("===> FAILED to copy:", incl)
            print("===> reason:", e)
            sys.exit(1)

    print("---> copied includes")

    
    requirement_dirs = {name: get_workdir(req_wf, parent_wfpath=wf_path) for req_wf, name in workflow["requires_names"].items()}
    requirement_dirs = json.dumps(requirement_dirs)


    print("---> run param_generator ... ", end="", flush=True)

    if("PYTHONPATH" in os.environ):
        pythonpath = ":".join((os.environ["PYTHONPATH"], os.path.join(full_workdir, "includes")))
    else:
        pythonpath = os.path.join(full_workdir, "includes")

    process = subprocess.run([os.path.join("..", workflow["param_generator"])]
                   , stdout=subprocess.PIPE
                   , stderr=subprocess.PIPE
                   , env={"PYTHONPATH": pythonpath
                          , "ESIS2_REQUIREMENTS": requirement_dirs}
                   , cwd=os.path.join(full_workdir, "parameters"))
    if(process.returncode == 0):
        print("OK")
    else:
        print("FAILED")

        print("===>", process.stderr)
        print("===>", process.stdout)
        print("===> terminating.")
        sys.exit(2)

    nparams = int(process.stdout) 
    print("---> generated", nparams + 1, "parameters.")

    print("---> running setup ... ", end="", flush=True)
    process = subprocess.run([os.path.join(".", workflow["setupscript"])]
                   , stdout=subprocess.PIPE
                   , stderr=subprocess.PIPE
                   , cwd=full_workdir)
    if(process.returncode == 0):
        print("OK")
    else:
        print("FAILED")

        print("===>", process.stderr)
        print("===>", process.stdout)
        print("===> terminating.")
        sys.exit(2)

    task_array_definition = f"0-{nparams}%{workflow['maxparallel']}"
    workerscript = os.path.join("..", workflow["workerscript"])
    if(len(afterok)):
        esis_private = "SBATCH --dependency=afterok:" + ":".join(str(jid) for jid in afterok)
    else:
        esis_private = ""
    with open(os.path.join(workflow_dir, workflow["sbatchtemplate"]), "r") as fin:
        with open(os.path.join(full_workdir, "sbatch.sh"), "w") as fout:
            for line in fin:
                fout.write(line.replace("TASKARRAYDEFINITION", task_array_definition).replace("WORKERSCRIPT", workerscript).replace("ESIS_PRIVATE", esis_private))
    print("---> created sbatch script")

    create_readme(os.path.join(full_workdir, "README"), os.path.abspath(wf_in_name))
    shutil.copy(wf_in_name, os.path.join(esis_private_dir, "workflow_definition.json"))


    print("---> running sbatch ... ", end="", flush=True)
    process = subprocess.run(["sbatch", os.path.join("..", "sbatch.sh")]
                             , cwd=os.path.join(full_workdir, "cwd")
                             , stdout=subprocess.PIPE
                             , stderr=subprocess.PIPE)
    if(process.returncode == 0):
        print("OK")
    else:
        print("FAILED")

        print("===>", process.stderr)
        print("===>", process.stdout)
        print("===> terminating.")
        sys.exit(2)

    # FIXME: this is hacky.
    for line in process.stdout.split(b"\n"):
        if(line.startswith(b"Submitted batch job")):
            jobid = int(line.split(b" ")[3])
    
    print("---> jobid:", jobid)

    with open(os.path.join(esis_private_dir, "jobid.tx"), "w") as fout:
        print(jobid, file=fout)

    return jobid

def create_readme(fname, wf_in_name):
    text = f'''
README
******

This directory is the working directory of a 
(semi) isolated workflow. It was automatically created and the 
job is currently either running or has finished running.

- The jobid of the SLURM job should be in ``__esis__/jobid.tx``.
- The logs are in ``cwd``.
- The original workflow definition file has been copied 
  to ``__esis__/workflow_definition.json``. Note that the original workflow 
  definition was in a different location, notably in ``{wf_in_name}``.
  Therefore, relative paths will be broken.
- Inspect ``sbatch.sh`` for more information.
- Some processes may create the file ``__esis__/completed.state``.
  If this file contains a ``1``, this indicates that the workflow finished 
  and all required output has been produced. Its absence indicates 
  that either the process omitted creating it or did not finish it.
  Inspect the code to obtain more information.


To (re)run the job run:: 

    cd cwd 
    sbatch ../sbatch.sh

    '''

    with open(fname, "w") as fout:
        print(text, file=fout)


def run(arguments):
    wf_in_name = arguments["<workflowfile>"]
    if(wf_in_name is None):
        wf_in_name = arguments["--workflow-out"]

    run_workflow(wf_in_name)

