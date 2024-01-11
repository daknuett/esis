#!/usr/bin/env python3

def list_requirements(arguments):
    wf_in_name = arguments["<workflowfile>"]
    if(wf_in_name is None):
        wf_in_name = arguments["--workflow-out"]

    if(not os.path.exists(wf_in_name)):
        print("===> FATAL: missing input workflow:", wf_in_name)
        sys.exit(1)

    with open(wf_in_name, "r") as fin:
        workflow = json.load(fin)

    
