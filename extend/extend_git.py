#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @brief: publish module to maven
# @date:   2023.08.10 14:40:50

import sys, os

g_this_file = os.path.realpath(sys.argv[0])
g_this_path = os.path.dirname(g_this_file)
sys.path.append(os.path.dirname(g_this_path))

from utils.utils_cmn import CmnUtils
from utils.utils_logger import LoggerUtils
from utils.utils_file import FileUtils
from utils.utils_import import ImportUtils
from basic.git import BasicGit
from basic.space import BasicSpace
from basic.arguments import BasicArgumentsValue
from extend.extend_base import ExtendBase

g_wing_path = ImportUtils.initEnv()


# --------------------------------------------------------------------------------------------------------------------------
def printLine(a, b, c=None):
    if CmnUtils.isEmpty(b) or b == 'null':
        b, c = None, None
    LoggerUtils.printColorTexts(a, LoggerUtils.GREEN,
                                b, LoggerUtils.RED_GRAY,
                                c, LoggerUtils.BLUE_GRAY
                                )

def printResults(results, gapFmt):
    if CmnUtils.isEmpty(results):
        LoggerUtils.w('No git repository found')
        return

    for result in results:
        title = LoggerUtils.alignLine(result[0])
        if CmnUtils.isEmpty(result[2]) or result[1] == result[2]:
            printLine(title, result[1])
        else:
            printLine(title, result[1], gapFmt % result[2])


def printPushResults(results):
    if CmnUtils.isEmpty(results):
        LoggerUtils.w('Everything up-to-date')
        return
    for result in results:
        title = LoggerUtils.alignLine(result[0])
        if result[2]:
            printLine(title, ' -> ' + result[1], ' : Success')
        else:
            printLine(title, ' -> ' + result[1], ' : Fail')


class ExtendBranch(ExtendBase):
    def __init__(self, path, results):
        ExtendBase.__init__(self, path)
        self.mResults = results

    def onProjectCall(self, space, project):
        pname = project.getPath()
        projPath = self.mBaseSpacePath + os.sep + pname
        if len(self.mResults) <= 0:
            self.parseBranch(g_wing_path, '.wing/wing')
            self.parseBranch(self.mBaseSpacePath + os.sep + '.wing/manifests', '.wing/manifests')
        remote = project.getRevision()
        if CmnUtils.isEmpty(remote): remote = space.getBranch()
        self.parseBranch(projPath, pname, remote)

    def parseBranch(self, projPath, pname, remote=None):
        git = BasicGit(projPath)
        branch = git.getCurrentBranch()
        branch = 'null' if CmnUtils.isEmpty(branch) else branch
        self.mResults.append([pname, branch, remote])


class ExtendStatus(ExtendBase):
    def __init__(self, path, results):
        ExtendBase.__init__(self, path)
        self.mResults = results

    def onProjectCall(self, space, project):
        pname = project.getPath()
        projPath = self.mBaseSpacePath + os.sep + pname
        if len(self.mResults) <= 0:
            self.parseBranch(g_wing_path, '.wing/wing')
            self.parseBranch(self.mBaseSpacePath + os.sep + '.wing/manifests', '.wing/manifests')
        remote = project.getRevision()
        if CmnUtils.isEmpty(remote): remote = space.getBranch()
        self.parseBranch(projPath, pname, remote)

    def parseBranch(self, projPath, pname, remote=None):
        git = BasicGit(projPath)
        status = 'changed' if git.isChanged() else ''
        branch = git.getCurrentBranch()
        branch = 'null' if CmnUtils.isEmpty(branch) else branch
        self.mResults.append([pname, branch, status])


def pushToRemoteGit(gitPath, isForce):
    git = BasicGit(gitPath)
    if not git.isAheadOfRemote(): return -1, None
    branch = None
    try:
        branch = git.getCurrentRemoteBranch()
        assert None != branch, 'Not found remote server branch'
        if isForce:
            git.pushCodeToServer(branch)
        else:
            git.pushCodeToGerrit(branch)
        return 1, branch
    except Exception as e:
        LoggerUtils.e(e)
    return 0, branch if None != branch else 'None'


class ExtendPush(ExtendBase):
    def __init__(self, path, isForce, results):
        ExtendBase.__init__(self, path)
        self.isForce = isForce
        self.mResults = results

    def onProjectCall(self, space, project):
        pname = project.getPath()
        projPath = self.mBaseSpacePath + os.sep + pname
        if len(self.mResults) <= 0:
            self.doPush(g_wing_path, '.wing/wing')
            self.doPush(self.mBaseSpacePath + os.sep + '.wing/manifests', '.wing/manifests')
        self.doPush(projPath, pname)

    def doPush(self, gitPath, pname):
        ret, branch = pushToRemoteGit(gitPath, self.isForce)
        if ret < 0: return
        self.mResults.append([pname, branch, 1 == ret])


def pushGroupToRemote(spacePath, envPath, projPath, isForce):
    results = []
    git = BasicGit(envPath)
    if git.isValidGit():
        ret, branch = pushToRemoteGit(envPath, isForce)
        if 0 <= ret: results.append([projPath[len(spacePath) + 1:], branch, 1 == ret])
    else:
        ep = ExtendPush(spacePath, isForce, results)
        ep.doActionWithManifest(True)
    printPushResults(results)


def doUpdateManifest(spacePath, baseBranch, newBranch):
    '''
    <default revision="main" remote="origin" sync-j="4"/>
    '''
    path = spacePath + '/.wing/manifests'
    try:
        for root, dirs, files in os.walk(path):
            for f in files:
                filename = os.path.join(root, f)
                if not filename.endswith('.xml'): continue
                with open(filename, 'r') as ff:
                    lines = ff.readlines()
                with open(filename, 'w') as ff:
                    for line in lines:
                        l = line.strip()
                        if l.startswith('<default '):
                            pos = l.find('revision')
                            assert 0 < pos, 'invalid revision: ' + l
                            l = l[pos + 9:]
                            pos = l.find('"')
                            l = l[pos + 1:]
                            pos = l.find('"')
                            branch = l[:pos]
                            line = line.replace('"' + branch + '"', '"' + newBranch + '"')
                        ff.write(line)

        ret = CmnUtils.doCmd('cd %s && git status' % (path))
        LoggerUtils.println(ret)
        if 0 < ret.find('nothing to commit'): return
        CmnUtils.doCmdCall('cd %s && git add .' % (path))
        CmnUtils.doCmdCall('cd %s && git commit -m "create %s from %s"' % (path, baseBranch, newBranch))
        ret = CmnUtils.doCmd('cd %s && git push origin HEAD:refs/heads/%s' % (path, newBranch))
        LoggerUtils.println(ret)
        assert 0 < ret.find(' done'), "manifest commit fail"
    except Exception as e:
        LoggerUtils.exception(e)
        CmnUtils.doCmdCall('cd %s && git stash' % (path))
        CmnUtils.doCmdCall('cd %s && git reset' % (path))
        assert 0


def doCreateProject(spacePath, baseBranch, newBranch, buildNo, project):
    LoggerUtils.light(project + ' -> ' + newBranch)
    git = BasicGit(spacePath + os.sep + project)
    git.fetchBranch(baseBranch, False)
    rbs = git.getRemoteBranches()
    if None == rbs or newBranch not in rbs:
        git.pushToRemoteBranch(newBranch)
    git.fetchBranch(newBranch, False)
    cfg = spacePath + os.sep + project + '/branchCreator.py'
    if not os.path.exists(cfg): return
    succ = CmnUtils.doCmdCall('cd "%s" && python "%s" %s %s %s' % (os.path.dirname(cfg), os.path.basename(cfg), baseBranch, newBranch, buildNo))
    assert succ, 'Error: Update version fail ' + project


def doCreate(spacePath, baseBranch, newBranch, buildNo):
    space = BasicSpace(spacePath)
    # space.println()
    projects = space.getManifestProjects()

    # do to projects
    for project in projects:
        if not CmnUtils.isEmpty(project.getRevision()): continue
        doCreateProject(baseBranch, newBranch, buildNo, project.getPath())

    # do to manifest
    doCreateProject(spacePath, baseBranch, newBranch, buildNo, '.wing/manifests')
    # update manifest
    doUpdateManifest(spacePath, baseBranch, newBranch)
    # update space config
    space.updateBranch(newBranch)


def doClean(spacePath):
    path = spacePath + '/out'
    if not os.path.isdir(path): return
    # clean cache results
    FileUtils.remove(path)
    # ff = os.listdir(path)
    # for f in ff:
    #     fileName = path + os.path.sep + f
    #     if not os.path.isfile(fileName): continue
    #     if f == 'build-info.txt':
    #         os.remove(fileName)
    #         continue
    #     if fileName.find('_to_') < 0: continue
    #     os.remove(fileName)


def doFlush(spacePath, baseBranch, newBranch, buildNo):
    path = spacePath + '/out'
    FileUtils.ensureDir(path)

    with open(path + '/' + baseBranch + '_to_' + newBranch, 'w') as f: f.write('')
    with open(path + '/build-info.txt', 'w') as f: f.write(baseBranch + ',' + newBranch + ',' + buildNo)


def createBranch(spacePath, baseBranch, newBranch, buildNo):
    LoggerUtils.light('Create branch: ' + baseBranch + ' -> ' + newBranch + ': ' + buildNo)
    doClean()
    doCreate(spacePath, baseBranch, newBranch, buildNo)
    doFlush(spacePath, baseBranch, newBranch, buildNo)


def run():
    argv = BasicArgumentsValue()
    envPath, spacePath, projPath, cmd = argv.get(0), argv.get(1), argv.get(2), argv.get(3)

    if '-branch' == cmd:
        results = []
        eb = ExtendBranch(spacePath, results)
        eb.doActionWithManifest(True)
        printResults(results, ' ≠ %s(remote)')
        return
    if '-push' == cmd:
        pushGroupToRemote(spacePath, envPath, projPath, 'f' == argv.get(3))
        return
    if '-newbranch' == cmd:
        buildNo = argv.get(5) if 5 < argv.count() else '0'
        createBranch(spacePath, argv.get(3), argv.get(4), buildNo)
        return
    if '-status' == cmd:
        results = []
        eb = ExtendStatus(spacePath, results)
        eb.doActionWithManifest(True)
        printResults(results, ' : %s')
        return
    LoggerUtils.e('UNsupport command: ' + cmd)


if __name__ == "__main__":
    run()
