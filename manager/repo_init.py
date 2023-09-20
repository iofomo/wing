# -*- encoding:utf-8 -*-
# @brief:  ......
# @date:   2023.05.10 14:40:50

import os
import sys

g_this_file = os.path.realpath(sys.argv[0])
g_this_path = os.path.dirname(g_this_file)
sys.path.append(os.path.dirname(g_this_path))

from utils.utils_file import FileUtils
from utils.utils_logger import LoggerUtils
from utils.utils_import import ImportUtils
from manager.repo_env import RepoEnv
from manager.repo_git import RepoGit
from manager.repo_sync import RepoSync
from manager.repo_config import RepoConfig

g_env_path, g_this_file, g_this_path = ImportUtils.initEnv()


# -----------------------------------------------------------------------------------------------------------------------------
def convert(gits, groupName, isKey=True):
    if isKey:
        if groupName in gits: return gits[groupName]
        return groupName
    return groupName


def exportXml(f, name):
    contents = [
        '<?xml version="1.0" encoding="UTF-8"?>\n',
        '<manifest>\n',
        '<include name="%s" />\n' % name,
        '</manifest>\n'
    ]
    with open(f, 'w') as f: f.writelines(contents)


def fetchManifest(rootPath, project, branch, xml):
    localProject = '.repo' + os.sep + 'manifests'
    # fetch
    exist = RepoGit.fetchGit(localProject, project)
    # switch branch
    LoggerUtils.light(project)
    RepoGit.fetchBranch('.repo/manifests', branch, True, False, not exist)
    assert RepoGit.checkBranch('.repo/manifests', branch), 'check manifests branch fail'

    # bind remote branch
    # RepoGit.bindBranchToRemote('.repo/manifests', branch)

    # export xml
    indexXml = rootPath + os.sep + '.repo' + os.sep + 'manifest.xml'
    exportXml(indexXml, xml)
    assert os.path.isfile(indexXml), 'export manifest.xml fail'


def switchBranch(path, branch):
    RepoEnv.init(path)
    fetchManifest(path, convert(RepoConfig.getGits(), RepoEnv.getGroupName()), branch, RepoEnv.getManifest())
    RepoSync.doSync(True, False, True)
    RepoEnv.setRepoBranch(branch)


def run():
    path, groupName, branch, manifest = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
    RepoEnv.init(path)
    RepoEnv.setGroupName(convert(RepoConfig.getGits(), groupName, False))
    RepoEnv.setManifest(manifest)
    RepoEnv.setRepoBranch(branch)
    FileUtils.remove(RepoEnv.getRootPath() + os.sep + 'out')  # clear out
    fetchManifest(path, convert(RepoConfig.getGits(), groupName), branch, manifest)
    RepoSync.doSync(True, False)


if __name__ == "__main__":
    run()
