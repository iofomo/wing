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
from framework.wing_env import WingEnv

g_wing_path = ImportUtils.initEnv()


# --------------------------------------------------------------------------------------------------------------------------
def printLine(a, b, c=None):
    if CmnUtils.isEmpty(b) or b == 'null':
        b, c = None, None
    LoggerUtils.printColorTexts(a, LoggerUtils.GREEN,
                                b, LoggerUtils.BLUE_GRAY,
                                c, LoggerUtils.RED_GRAY
                                )


def printResults(results, gapFmt, defRes=''):
    if CmnUtils.isEmpty(results):
        LoggerUtils.w('No git repository found')
        return

    for result in results:
        title = LoggerUtils.alignLine(result[0])
        if CmnUtils.isEmpty(result[2]) or result[1] == result[2]:
            printLine(title, result[1] if CmnUtils.isEmpty(result[1]) or result[1] == 'null' else result[1] + defRes)
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


def isGitManifest(manifestsPath):
    return BasicGit(manifestsPath).isValidGit()


class ExtendBranch(ExtendBase):
    def __init__(self, path, results):
        ExtendBase.__init__(self, path)
        self.mResults = results

    def onProjectCall(self, space, project):
        pname = project.getPath()
        projPath = self.mBaseSpacePath + os.sep + pname
        if len(self.mResults) <= 0:
            # self.parseBranch(g_wing_path, '.wing/wing')
            manifestsPath = self.mBaseSpacePath + os.sep + '.wing/manifests'
            if isGitManifest(manifestsPath):
                self.parseBranch(manifestsPath, '.wing/manifests', space.getBranch())
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
            manifestsPath = self.mBaseSpacePath + os.sep + '.wing/manifests'
            if isGitManifest(manifestsPath):
                self.parseBranch(manifestsPath, '.wing/manifests')
        remote = project.getRevision()
        if CmnUtils.isEmpty(remote): remote = space.getBranch()
        self.parseBranch(projPath, pname)

    def parseBranch(self, projPath, pname):
        git = BasicGit(projPath)
        _, status = git.getStatus()
        branch = git.getCurrentBranch()
        branch = 'null' if CmnUtils.isEmpty(branch) else branch
        self.mResults.append([pname, branch, status])


def pushToRemoteGit(gitPath, isForce):
    git = BasicGit(gitPath)
    if not git.isAheadOfRemote(): return -1, None
    branch = None
    try:
        branch = git.getCurrentRemoteBranch()
        assert branch is not None, 'Not found remote server branch'
        if isForce:
            git.pushCodeToServer(branch)
        else:
            git.pushCodeToReview(branch)
        return 1, branch
    except Exception as e:
        LoggerUtils.e(e)
    return 0, branch if branch is not None else 'None'


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
            manifestsPath = self.mBaseSpacePath + os.sep + '.wing/manifests'
            if isGitManifest(manifestsPath):
                self.doPush(manifestsPath, '.wing/manifests')
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
                LoggerUtils.println("update: " + f)

        BasicGit(path).pushCommitToServer(newBranch, "create %s from %s" % (baseBranch, newBranch))
        LoggerUtils.println("push manifests to remote")
    except Exception as e:
        LoggerUtils.exception(e)
        assert 0


def doCreateBranch(spacePath, project, baseBranch, newBranch):
    LoggerUtils.light(project + ' -> ' + newBranch)
    git = BasicGit(spacePath + os.sep + project)
    git.fetchBranch(baseBranch, False)
    git.pushToRemoteBranch(newBranch)
    return git


def doCreateTag(spacePath, project, baseBranch, newTag, msg):
    LoggerUtils.light(project + ' -> ' + newTag)
    git = BasicGit(spacePath + os.sep + project)
    git.fetchBranch(baseBranch, False)
    git.pushToRemoteTag(newTag, msg)


def doCreateBranches(envPath, spacePath, baseBranch, newBranch):
    space = BasicSpace(spacePath)
    # space.println()
    projects = space.getManifestProjects()

    # do to projects
    for project in projects:
        if not CmnUtils.isEmpty(project.getRevision()):
            LoggerUtils.w('ignore: ' + project.getPath() + ', has revision')
            continue
        doCreateBranch(spacePath, project.getPath(), baseBranch, newBranch)

    if isGitManifest(spacePath + os.sep + '.wing/manifests'):
        LoggerUtils.println("do update manifests")
        # do to manifest
        git = doCreateBranch(spacePath, '.wing/manifests', baseBranch, newBranch)
        git.fetchBranch(newBranch, False)
        # update manifest
        doUpdateManifest(spacePath, baseBranch, newBranch)
        WingEnv.init(spacePath, envPath)
        WingEnv.setSpaceBranch(newBranch)
        LoggerUtils.light("Space is " + newBranch + " now !")


def doCreateTages(spacePath, baseBranch, newTag, msg):
    space = BasicSpace(spacePath)
    # space.println()
    projects = space.getManifestProjects()

    # do to projects
    for project in projects:
        if not CmnUtils.isEmpty(project.getRevision()): continue
        doCreateTag(spacePath, project.getPath(), baseBranch, newTag, msg)

    # do to manifest
    if isGitManifest(spacePath + os.sep + '.wing/manifests'):
        doCreateTag(spacePath, '.wing/manifests', baseBranch, newTag, msg)


def doFlush(spacePath, baseBranch, newBranch):
    path = spacePath + '/out'
    FileUtils.ensureDir(path)

    with open(path + '/' + baseBranch + '_to_' + newBranch, 'w') as f: f.write('')
    with open(path + '/build-info.txt', 'w') as f: f.write(baseBranch + ',' + newBranch)


def createTag(spacePath, newTag, baseBranch, msg):
    LoggerUtils.light('Create workspace tag: ' + baseBranch + ' -> ' + newTag)
    doCreateTages(spacePath, baseBranch, newTag, msg)


def createBranch(envPath, spacePath, newBranch, baseBranch):
    LoggerUtils.light('Create workspace branch: ' + baseBranch + ' -> ' + newBranch)
    doCreateBranches(envPath, spacePath, baseBranch, newBranch)
    doFlush(spacePath, baseBranch, newBranch)


def run():
    argv = BasicArgumentsValue()
    envPath, spacePath, projPath, cmd = argv.get(0), argv.get(1), argv.get(2), argv.get(3)

    if '-branch' == cmd:
        results = []
        eb = ExtendBranch(spacePath, results)
        eb.doActionWithManifest(True)
        printResults(results, ' ≠ %s(remote)', ' (no changes)')
        return
    if '-push' == cmd:
        # wing -push [f]
        pushGroupToRemote(spacePath, envPath, projPath, 'f' == argv.get(4))
        return
    if '-create' == cmd:
        # wing -create t {new tag name} {base branch name} [tag message]
        # wing -create b {new branch name} {base branch name}
        arg = argv.get(4)
        if arg == 't':
            createTag(spacePath, argv.get(5), argv.get(6), argv.get(7))
        elif arg == 'b':
            createBranch(envPath, spacePath, argv.get(5), argv.get(6))
        return
    if '-status' == cmd:
        results = []
        eb = ExtendStatus(spacePath, results)
        eb.doActionWithManifest(True)
        printResults(results, ' : %s', ' (nothing to commit)')
        return
    LoggerUtils.e('UNsupport command: ' + cmd)


if __name__ == "__main__":
    run()
