# -*- encoding:utf-8 -*-
# @brief:  ......
# @date:   2023.05.10 14:40:50

import os
from utils.utils_cmn import CmnUtils
from utils.utils_file import FileUtils


# -------------------------------------------------------------
class WingEnv:
    g_space_path = None
    g_space_name = None
    g_space_branch = None
    g_space_manifest = None
    g_wing_path = None
    g_remote_host = None
    g_remote_manifest = None
    g_env_path = None


    @classmethod
    def init(cls, spacePath, envPath):
        cls.g_space_path = spacePath
        cls.g_env_path = envPath
        cls.doLoad()

    @classmethod
    def getSpacePath(cls):
        return cls.g_space_path

    @classmethod
    def getEnvPath(cls):
        return cls.g_env_path

    @classmethod
    def getWingPath(cls):
        if cls.g_wing_path is None:
            cls.g_wing_path = os.path.expanduser("~") + os.sep + '.wing/wing'  # such as: /Users/${username}/.wing/wing
        return cls.g_wing_path

    @classmethod
    def getSpaceName(cls):
        return cls.g_space_name

    @classmethod
    def setSpaceName(cls, v):
        cls.g_space_name = v
        cls.doSave()

    @classmethod
    def isLocalMode(cls):
        return cls.g_space_name == 'local'

    @classmethod
    def getSpaceManifestFile(cls):
        return cls.g_space_manifest

    @classmethod
    def setSpaceManifestFile(cls, v):
        cls.g_space_manifest = v
        cls.doSave()

    @classmethod
    def getSpaceBranch(cls):
        return cls.g_space_branch

    @classmethod
    def setSpaceBranch(cls, v):
        cls.g_space_branch = v
        cls.doSave()

    @classmethod
    def getSpaceConfigFile(cls):
        return cls.g_space_path + os.sep + '.wing' + os.sep + 'space.json'

    @classmethod
    def doSave(cls):
        cfg = {}
        if cls.g_space_name is not None: cfg['space'] = cls.g_space_name
        if cls.g_space_branch is not None: cfg['branch'] = cls.g_space_branch
        if cls.g_space_manifest is not None: cfg['manifest'] = cls.g_space_manifest
        # add more here ...
        FileUtils.saveJsonToFile(cls.getSpaceConfigFile(), cfg)

    @classmethod
    def doLoad(cls):
        cfg = FileUtils.loadJsonByFile(cls.getSpaceConfigFile())
        if None == cfg: return
        if 'space' in cfg: cls.g_space_name = cfg['space']
        if 'branch' in cfg: cls.g_space_branch = cfg['branch']
        if 'manifest' in cfg: cls.g_space_manifest = cfg['manifest']
        # add more here ...

    @classmethod
    def getSpaceRemoteManifestGit(cls):
        if cls.g_remote_manifest is None: cls.__do_load_config__()
        # assert cls.g_remote_manifest is not None, 'Error: Invalid space ' + cls.getSpaceName()
        return cls.g_remote_manifest

    @classmethod
    def getSpaceRemoteHost(cls):
        if cls.g_remote_host is None: cls.__do_load_config__()
        # assert cls.g_remote_host is not None, 'Error: Invalid space ' + cls.getSpaceName()
        return cls.g_remote_host

    @classmethod
    def __do_load_config__(cls):
        jdata = FileUtils.loadJsonByFile(cls.getWingPath() + '/res/config.json')
        spaces = jdata['space']
        if spaces is None: return None
        if cls.getSpaceName() not in spaces: return None
        space = spaces[cls.getSpaceName()]
        cls.g_remote_host = space['host']
        cls.g_remote_manifest = space['manifest']

    @staticmethod
    def isOsLinux():
        return CmnUtils.isOsLinux()

    @staticmethod
    def isOsWindows():
        return CmnUtils.isOsWindows()

    @staticmethod
    def isOsMac():
        return CmnUtils.isOsMac()
