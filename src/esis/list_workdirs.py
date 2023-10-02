#!/usr/bin/env python3

import os
import sys
import re

def read_workdir(pth):
    data = {"path": pth}

    # FIXME: legacy
    if(os.path.exists(os.path.join(pth, "jobid.tx"))):
        with open(os.path.join(pth, "jobid.tx")) as fin:
            data["jobid"] = fin.read().strip()
    if(os.path.exists(os.path.join(pth, "wf_starttime"))):
        with open(os.path.join(pth, "wf_starttime")) as fin:
            data["starttime"] = fin.read().strip()

    if(os.path.exists(os.path.join(pth, "__esis__", "jobid.tx"))):
        with open(os.path.join(pth, "__esis__", "jobid.tx")) as fin:
            data["jobid"] = fin.read().strip()
    if(os.path.exists(os.path.join(pth, "__esis__", "wf_starttime"))):
        with open(os.path.join(pth, "__esis__", "wf_starttime")) as fin:
            data["starttime"] = fin.read().strip()

    if("jobid" not in data):
        data["jobid"] = "0"
    if("starttime" not in data):
        data["starttime"] = "0"

    return data

def list_workdirs(arguments):
    path = "."
    if(arguments["<list-path>"] is not None):
        path = arguments["<list-path>"]

    if(not os.path.exists(path)):
        print("###>", path, "does not exist.")
        sys.exit(1)

    try:
        path_content = os.listdir(path)     
    except:
        print("###> could not list,", path)
        sys.exit(1)

    def filter_wd(pth):
        pattern = re.compile(r"wrkdir\.[a-f0-9]{64}/?")
        if(not pattern.match(os.path.basename(pth))):
            return False
        if(not os.path.isdir(pth)):
            return False
        return True


    workdirs = filter(filter_wd, path_content)

    workdir_info = [read_workdir(pth) for pth in workdirs]
    workdir_info = list(sorted(workdir_info, key=lambda wdi: wdi["path"]))

    if(arguments["--by-jobid"]):
        workdir_info = list(sorted(workdir_info, key=lambda wdi: wdi["jobid"]))
    if(arguments["--by-time"]):
        workdir_info = list(sorted(workdir_info, key=lambda wdi: wdi["starttime"]))

    for wdi in workdir_info:
        if(arguments["--by-time"]):
            print(wdi["starttime"], end="\t")
        if(arguments["--by-jobid"]):
            print(wdi["jobid"], end="\t")
        print(wdi["path"])

    return len(wdi)
