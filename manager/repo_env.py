# -*- encoding:utf-8 -*-
# @brief:  ......
# @date:   2023.05.10 14:40:50

import os
from utils.utils_cmn import CmnUtils
from utils.utils_file import FileUtils
from manager.repo_config import RepoConfig


# -------------------------------------------------------------
class RepoEnv:
    g_root_path = None
    g_group_name = None
    g_repo_branch = None
    g_manifest = None

    @classmethod
    def init(cls, rootPath):
        cls.g_root_path = rootPath
        cls.doLoad()
        RepoConfig.init(rootPath)

    @classmethod
    def getRootPath(cls):
        return cls.g_root_path

    @classmethod
    def getGroupName(cls):
        return cls.g_group_name

    @classmethod
    def setGroupName(cls, v):
        cls.g_group_name = v
        cls.doSave()

    @classmethod
    def getManifest(cls):
        return cls.g_manifest

    @classmethod
    def setManifest(cls, v):
        cls.g_manifest = v
        cls.doSave()

    @classmethod
    def getRepoBranch(cls):
        return cls.g_repo_branch

    @classmethod
    def setRepoBranch(cls, v):
        cls.g_repo_branch = v
        cls.doSave()

    @classmethod
    def getConfigFile(cls):
        return cls.g_root_path + os.sep + '.repo' + os.sep + 'cache.json'

    @classmethod
    def doSave(cls):
        cfg = {}
        if None != cls.g_group_name: cfg['group'] = cls.g_group_name
        if None != cls.g_repo_branch: cfg['branch'] = cls.g_repo_branch
        if None != cls.g_manifest: cfg['manifest'] = cls.g_manifest
        # add more here ...
        FileUtils.saveJsonToFile(cls.getConfigFile(), cfg)

    @classmethod
    def doLoad(cls):
        cfg = FileUtils.loadJsonByFile(cls.getConfigFile())
        if None == cfg: return
        if 'group' in cfg: cls.g_group_name = cfg['group']
        if 'branch' in cfg: cls.g_repo_branch = cfg['branch']
        if 'manifest' in cfg: cls.g_manifest = cfg['manifest']
        # add more here ...

    @staticmethod
    def isOsLinux():
        return CmnUtils.isOsLinux()

    @staticmethod
    def isOsWindows():
        return CmnUtils.isOsWindows()

    @staticmethod
    def isOsMac():
        return CmnUtils.isOsMac()
