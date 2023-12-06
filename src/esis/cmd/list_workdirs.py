#!/usr/bin/env python3

import os
import sys
import re
import datetime

from .const import dt_format_hr
from .status import get_workdir_name

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
        print("###> could not list", path)
        sys.exit(1)

    def filter_wd(pth):
        pattern = re.compile(r"wrkdir\.[a-f0-9]{64}/?")
        if(not pattern.match(os.path.basename(pth))):
            return False
        if(not os.path.isdir(os.path.join(path, pth))):
            return False
        return True

    def filter_wff(pth):
        pattern1 = re.compile(r"wf\.esis2.?.json")
        pattern2 = re.compile(r"wf\.bwfmitm2?\.json")
        if(not (pattern1.match(os.path.basename(pth))
                or pattern2.match(os.path.basename(pth)))):
            return False
        if(not os.path.isfile(os.path.join(path, pth))):
            return False
        return True

    workdirs = filter(filter_wd, path_content)
    wf_files = filter(filter_wff, path_content)

    current_names = [get_workdir_name(f) for f in wf_files]

    workdir_info = [read_workdir(os.path.join(path, pth)) for pth in workdirs]
    workdir_info = list(sorted(workdir_info, key=lambda wdi: wdi["path"]))

    if(arguments["--by-jobid"]):
        workdir_info = list(sorted(workdir_info, key=lambda wdi: int(wdi["jobid"])))
    if(arguments["--by-time"]):
        workdir_info = list(sorted(workdir_info, key=lambda wdi: datetime.datetime.strptime(wdi["starttime"], dt_format_hr)))

    for wdi in workdir_info:
        if(arguments["--by-time"]):
            print(wdi["starttime"], end="\t")
        if(arguments["--by-jobid"]):
            print(wdi["jobid"], end="\t")
        prefix = ""
        postfix = ""
        for cn in current_names:
            if cn in wdi["path"]:
                prefix = "\033[93;4m"
                postfix = "\033[0m"
        print(f'{prefix}{wdi["path"]}{postfix}')

    return len(workdir_info)
