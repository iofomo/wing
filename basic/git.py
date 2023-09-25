#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @brief:  Git project parser
# @date:   2023.05.10 14:40:50

import os, sys

g_this_file = os.path.realpath(sys.argv[0])
g_this_path = os.path.dirname(g_this_file)
sys.path.append(os.path.dirname(g_this_path))

from utils.utils_cmn import CmnUtils
from utils.utils_logger import LoggerUtils


# --------------------------------------------------------------------------------------------------------------------------
class BasicGit:

    def __init__(self, gitPath):
        self.mGitPath = gitPath

    def getCurrentBranch(self):
        branches = self.__doGitCmd__('branch')
        if None == branches: return None
        bb = branches.split('\n')
        for b in bb:
            b = b.strip()
            if not b.startswith('*'): continue
            b = b[1:].strip()
            return b
        return None

    def isChanged(self):
        ret = self.__doGitCmd__('status')
        for line in ret.split('\n'):
            line = line.strip()
            if CmnUtils.isEmpty(line): continue
            if line.startswith('nothing to commit'): return False
        return True

    def getCurrentRemoteBranch(self):
        branches = self.__doGitCmd__('branch -vv')
        if None == branches: return None
        bb = branches.split('\n')
        for b in bb:
            b = b.strip()
            if not b.startswith('* '): continue
            pos = b.find('[origin/')
            if 0 < pos:
                b = b[pos + len('[origin/'):]
                pos1 = b.find(']')
                pos2 = b.find(':')
                pos = pos2 if 0 < pos2 < pos1 else pos1
                if 0 < pos: return b[:pos]
            break
        return None

    def isAheadOfRemote(self):
        ret = self.__doGitCmd__('status')
        return ret is not None and 0 < ret.find(' is ahead of ')

    def isValidGit(self):
        ret = self.__doGitCmd__('status')
        return ret is not None and ret.find('not a git') < 0

    def getBranches(self):
        bbs = []
        branches = self.__doGitCmd__('branch')
        if branches is None: return bbs

        bb = branches.split('\n')
        for b in bb:
            b = b.strip()
            if len(b) <= 0: continue
            if not b.startswith('*'):
                bbs.append(b)
                continue
            b = b[1:].strip()
            bbs.append(b)
        return bbs

    def getOtherBranches(self):
        branches = self.__doGitCmd__('branch')
        if branches is None: return None

        bbs = []
        bb = branches.split('\n')
        for b in bb:
            b = b.strip()
            if len(b) <= 0: continue
            if b.startswith('*'): continue
            bbs.append(b)
        return bbs

    def hasBranch(self, branch):
        return branch in self.getBranches()

    def getRemoteBranches(self):
        branches = self.__doGitCmd__('branch -la')
        if branches is None: return None

        bbs = []
        bb = branches.split('\n')
        for b in bb:
            b = b.strip()
            if len(b) <= 0: continue
            if not b.startswith('remotes/origin/'): continue
            bbs.append(b[len('remotes/origin/'):])
        return bbs

    def __doGitCmd__(self, subCmd, ast=False):
        ret = CmnUtils.doCmd('cd %s && git %s' % (self.mGitPath, subCmd))
        if 0 <= ret.find('error:'):
            LoggerUtils.println(ret)
            if ast: assert 0, 'Fail: git ' + subCmd
        return ret

    def getServerName(self):
        s = self.__doGitCmd__('remote -v')
        ll = s.splitlines()
        for l in ll:
            pos = l.find('@')
            if pos <= 0: continue
            l = l[pos:]
            pos = l.find('/')
            if pos <= 0: continue
            l = l[pos + 1:]
            pos = l.find(' ')
            if pos <= 0: continue
            return l[:pos]
        return None

    def deleteBranch(self, branch):
        self.__doGitCmd__('branch -D ' + branch)
        assert not self.hasBranch(branch), 'Git delete branch fail: ' + branch

    def cleanCache(self):
        self.__doGitCmd__('rm -r --cached')

    def fetchBranch(self, branch, forceFetch=True):
        if not self.hasBranch(branch):
            ret = self.__doGitCmd__('fetch origin %s:%s' % (branch, branch), True)
            LoggerUtils.println(ret)

        frc = ' -f' if forceFetch else ''
        if self.hasBranch(branch):
            ret = self.__doGitCmd__('checkout%s %s' % (frc, branch))
        else:
            ret = self.__doGitCmd__('checkout%s -b %s origin/%s' % (frc, branch, branch))
        LoggerUtils.println(ret)

        currBranch = self.getCurrentBranch()
        assert currBranch == branch, 'Error: ' + currBranch + ' != ' + branch
        # self.setUpstream(currBranch)
        self.__doGitCmd__('pull origin %s' % (branch), True)

    def getVersion(self):
        ret = self.__doGitCmd__('--version')
        if None != ret:
            items = ret.split(' ')
            if 3 <= len(items):  # "git version 2.1.0"
                return items[2].strip()
        return None

    def isAboveV2(self):
        v = self.getVersion()
        if None != v:
            vv = v.split('.')
            return 2 <= int(vv[0])
        return False

    def setUpstream(self, branch):
        if not self.isAboveV2(): return
        ret = self.__doGitCmd__('branch -vv')
        if None != ret:
            items = ret.split('\n')
            for item in items:
                item = item.replace('*', '').strip()
                if not item.startswith(branch + ' '): continue
                if 0 < item.find('[origin/'): return  # has set
                break
        self.__doGitCmd__('branch --set-upstream-to=origin/%s %s' % (branch, branch))

    def pushToRemoteBranch(self, newBranch):
        branches = self.getRemoteBranches()
        assert None != branches and 0 < len(branches), 'Error: Invalid remote git server'
        if newBranch in branches: return  # remote branch exist
        self.__doGitCmd__('push origin HEAD:refs/heads/' + newBranch, True)
        branches = self.getRemoteBranches()
        assert newBranch in branches, 'Error: Remote branch create fail ' + newBranch

    def pushCodeToServer(self, branch):
        branches = self.getRemoteBranches()
        assert None != branches and 0 < len(branches), 'Error: Invalid remote git server'
        assert branch in branches, 'remote branch not exist: ' + branch
        self.__doGitCmd__('push origin HEAD:refs/heads/' + branch, True)
        assert not self.isAheadOfRemote(), 'error: push fail'

    def pushCodeToGerrit(self, branch):
        self.__doGitCmd__('push origin HEAD:refs/for/' + branch, True)
        # assert not self.isAheadOfRemote(), 'error: push fail'

    def println(self):
        LoggerUtils.println('Branches:', self.getBranches())
        LoggerUtils.println('Other branche:', self.getOtherBranches())
        LoggerUtils.println('Current branch:', self.getCurrentBranch())
        LoggerUtils.println('Remote branches:', self.getRemoteBranches())
        LoggerUtils.println('ServerName:', self.getServerName())


def run():
    git = BasicGit('/Users/xxx/workspace/demo', '/Users/xxx/workspace/demo/abc')
    git.println()


if __name__ == "__main__":
    run()
