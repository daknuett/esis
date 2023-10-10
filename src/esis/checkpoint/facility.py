"""
Checkpointing facility that provides automatic discovery of 
ESIS working directories and handling of checkpoints.
"""

import os
import typing

from .checkpoint import Checkpoint, IterativeCheckpoint

def get_default_external_storage_path():
    return f"/glurch/scratch/{os.environ['USER']}/esis_checkpoints"

class ChkPtFacility:
    def __init__(self, baseseed:typing.Union[str, int], external_storage_path=get_default_external_storage_path()):
        self._workdir = ChkPtFacility.get_workdir()
        self._ext_storage_path = external_storage_path
        self._baseseed = baseseed

    def has_checkpoint(self, name):
        return Checkpoint.is_OK(name, self._workdir)

    def create_checkpoint(self, name):
        return Checkpoint.create(name, self._workdir, self._ext_storage_path, self._baseseed)

    def set_run_OK(self):
        with open(os.path.join(self._workdir, "__esis__", "completed.state"), "w") as status_file:
            status_file.write("1")

    def load_checkpoint(self, name):
        return Checkpoint.load(name, self._workdir)

    def has_iterative_checkpoint(self, name):
        return IterativeCheckpoint.exists(name, self,_workdir)

    def create_iterative_checkpoint(self, name):
        return IterativeCheckpoint.create(name, self._workdir, self._ext_storage_path, self._baseseed)

    def iterative_checkpoint_is_finished(self, name):
        return IterativeCheckpoint.is_OK(name, self._workdir)

    def open_iterative(self, name):
        return IterativeCheckpoint.load(name, self._workdir)

    @classmethod
    def get_workdir(cls):
        cwd = os.getcwd()
        # A very simple (but very time accurate guess) is the following 
        # directory structure:
        #   wd/           < this is the workdir
        #      cwd/       < you are here
        #      __esis__/  < you are looking for this.

        if(os.path.exists(os.path.join(cwd, "..", "__esis__"))):
            return os.path.abspath(os.path.join(cwd, ".."))

        # less common
        if(os.path.exists(os.path.join(cwd, "__esis__"))):
            return cwd

        # We have to search
        while cwd != "/":
            cwd = os.path.abspath(os.path.join(cwd, ".."))
            if(os.path.exists(os.path.join(cwd, "__esis__"))):
                return cwd

        raise ValueError("failed to find esis workdir")

        
