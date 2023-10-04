#!/usr/bin/env python3

"""
Checkpointing facility.

Requirements: 
    - data storage both internal and external
    - keep track of whether or not a checkpoint has been reached.

"""

import os
import datetime
import json

from ..cmd.const import dt_format_hr

class Checkpoint:
    checkpoint_dir =  "__checkpoints__"
    storage_dir = "storage"
    state_OK_name = "checkpoint.ok"
    meta_file_name = "checkpoint.meta.json"
    external_link_name ="external"
    def __init__(self
                 , name
                 , external_storage_path
                 , internal_path
                 , internal_storage_path
                 , chkpt_ok_fname
                 , workdir_name
                 , ext_link_name):
        self._name = name
        self._external_storage_path = external_storage_path

        self._internal_path = internal_path
        self._internal_storage_path = internal_storage_path
        self._chkpt_ok_fname = chkpt_ok_fname
        self._workdir_name = workdir_name
        self._ext_link_name = ext_link_name

    @classmethod 
    def create(cls, name, workdir_root, external_storage_path):
        if(cls.exists(name, workdir_root)):
            raise ValueError(f"checkpoint {name} exists.")

        internal_path = os.path.join(workdir_root, cls.checkpoint_dir, name)
        storage_path = os.path.join(internal_path, cls.storage_dir)
        os.makedirs(storage_path)

        now = datetime.datetime.now()
        meta = {
                "__type__": cls.__name__
                , "created_on": now.strftime(dt_format_hr)
                , "original_internal": internal_path
                , "storage_rela": cls.storage_dir
                , "state_OK_file": cls.state_OK_name
                , "external_storage_path": external_storage_path
                , "workdir_name": os.path.basename(os.path.abspath(workdir_root))
                , "external_link_name": cls.external_link_name
        }

        with open(os.path.join(internal_path, cls.meta_file_name), "w") as fout:
            json.dump(meta, fout)

        return cls.load(name, workdir_root)
    

    @classmethod
    def load(cls, name, workdir_root):
        if(not cls.exists(name, workdir_root)):
            raise ValueError(f"checkpoint {name} does not exist.")

        internal_path = os.path.join(workdir_root, cls.checkpoint_dir, name)
        meta_file = os.path.join(internal_path, cls.meta_file_name)

        with open(meta_file) as fin:
            meta = json.load(fin)

        return cls(name
                   , meta["external_storage_path"]
                   , internal_path
                   , os.path.join(internal_path, meta["storage_rela"])
                   , os.path.join(internal_path, meta["state_OK_name"])
                   , meta["workdir_name"]
                   , meta["ext_link_name"])

    

    @classmethod
    def exists(cls, name, workdir_root):
        internal_path = os.path.join(workdir_root, cls.checkpoint_dir)
        chkpt_path = os.path.join(internal_path, name)

        if(not os.path.exists(chkpt_path)):
            return False
        if(not os.path.exists(os.path.join(chkpt_path, cls.meta_file_name))):
            return False
        return True

    @classmethod
    def is_OK(cls, name, workdir_root):
        if(not cls.exists(name, workdir_root)):
            return False

        state_path = os.path.join(workdir_root, cls.checkpoint_dir, name, cls.state_OK_name)
        
        if(not os.path.exists(state_path)):
            return False
        return True
        
    def get_external_storage_path(self):
        return os.path.join(self._external_storage_path, self._workdir_name)

    def create_external_path_if_not_exists(self):
        pathname = self.get_external_storage_path()
        if(not os.path.exists(pathname) and not os.path.exists(os.path.join(self._internal_path, self._ext_link_name))):
            os.path.makedirs(pathname)
            os.symlink(pathname, os.path.join(self._internal_path, self._ext_link_name))


    def get_file_name(self, data_name, store_external=False):
        if(not store_external):
            return os.path.join(self._internal_storage_path, data_name)

        self.create_external_path_if_not_exists()

        return os.path.join(self._internal_path, self._ext_link_name, data_name)


    def set_OK(self):
        fname = os.path.join(self._internal_path, self._chkpt_ok_fname)
        with open(fname, "w") as fout:
            print("1",file=fout)
