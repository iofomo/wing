# -*- encoding:utf-8 -*-
# @brief:  ......
# @date:   2023.05.10 14:40:50

from utils.utils_file import FileUtils


# --------------------------------------------------------------------------------------------------------------------------
class RepoConfig:
    g_gits = None
    g_git_remote_host = None

    @classmethod
    def init(cls, repoPath):
        jdata = FileUtils.loadJsonByFile(repoPath + '/.repo/repo/config.json')
        cls.g_gits = jdata['group']
        jremote = jdata['remote']
        cls.g_git_remote_host = jremote['host'] if 'host' in jremote else None

    @classmethod
    def getGits(cls): return cls.g_gits

    @classmethod
    def getGitRemoteHost(cls): return cls.g_git_remote_host

    # @classmethod
    # def getGitRemoteID(cls): return cls.g_git_remote_id
