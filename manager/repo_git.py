# -*- encoding:utf-8 -*-
# @brief:  ......
# @date:   2023.05.10 14:40:50

import os, sys, shutil

g_this_file = os.path.realpath(sys.argv[0])
g_this_path = os.path.dirname(g_this_file)
sys.path.append(os.path.dirname(g_this_path))

from utils.utils_cmn import CmnUtils
from utils.utils_file import FileUtils
from utils.utils_logger import LoggerUtils
from utils.utils_import import ImportUtils
from manager.repo_env import RepoEnv
from manager.repo_config import RepoConfig

g_env_path, g_this_file, g_this_path = ImportUtils.initEnv()
g_repo_path = ImportUtils.initPath(g_env_path)


# ------------------------------------------------------------------------------------------------------------------------
class RepoGit:
    @staticmethod
    def getGitProjects():
        projects = []
        lastPath = ''
        l = len(RepoEnv.getRootPath())
        for root, dirs, files in os.walk(RepoEnv.getRootPath()):
            for dir in dirs:
                sub = os.path.join(root, dir)
                if 0 < len(lastPath) and sub.startswith(lastPath): continue
                if not os.path.isdir(sub + os.path.sep + '.git'): continue
                lastPath = sub + os.path.sep
                ends = sub[l + 1:]
                if ends == '.repo/repo': continue
                projects.append(ends)
        return projects

    @staticmethod
    def exeCmdToGitsByStatus(project, ret):
        branch, ok = '', None
        items = ret.split('\n')
        for item in items:
            item = item.strip()
            if item.startswith('On branch '):
                branch = item[len('On branch') + 1:].strip()
                continue
            if item.startswith('nothing to commit'):
                ok = ''
                continue
        LoggerUtils.printLine(LoggerUtils.alignLine(project), branch, ok)
        if None == ok: LoggerUtils.println(ret)

    @staticmethod
    def exeCmdToGits(cmd):
        projects = RepoGit.getGitProjects()
        for project in projects:
            try:
                ret = RepoGit.exeCmdToGit(project, cmd)
                if 0 <= ret.find('error'):
                    LoggerUtils.e(project + ' : Failed')
                    continue
                if 'status' == cmd:
                    RepoGit.exeCmdToGitsByStatus(project, ret)
                    continue
                LoggerUtils.println(ret)
            except Exception as e:
                # LoggerUtils.println(e)
                LoggerUtils.e(project + ' : Failed')
                assert 0, 'except'

    @staticmethod
    def exeCmdToGit(project, cmd):
        path = RepoEnv.getRootPath() + os.path.sep + project
        ret = CmnUtils.doCmd('cd %s && git %s' % (path, cmd))
        # LoggerUtils.println(ret)
        if 0 <= ret.find('error'): LoggerUtils.error(ret)
        return ret

    @staticmethod
    def gitVersion(path):
        ret = CmnUtils.doCmd('cd %s && git --version' % (path))
        if None != ret:
            items = ret.split(' ')
            if 3 <= len(items):  # "git version 2.1.0"
                return items[2].strip()
        return None

    @staticmethod
    def isAboveV2(path):
        v = RepoGit.gitVersion(path)
        if None != v:
            vv = v.split('.')
            return 2 <= int(vv[0])
        return False

    @staticmethod
    def gitSetUpstream(project, branch):
        path = RepoEnv.getRootPath() + os.path.sep + project
        # if not RepoGit.isAboveV2(path): return
        ret = CmnUtils.doCmd('cd %s && git branch -vv' % (path))
        if None != ret:
            lines = ret.split('\n')
            for line in lines:
                line = line.strip()
                if not line.startswith('*'): continue
                if 0 < line.find('[origin/'): return  # has set
        RepoGit.bindBranchToRemote(project, branch)

    @staticmethod
    def checkBranch(project, branch):
        return branch == RepoGit.getCurrentBranch(project)

    @staticmethod
    def bindBranchToRemote(project, branch):
        RepoGit.exeCmdToGit(project, 'branch --set-upstream-to=origin/%s %s' % (branch, branch))

    @staticmethod
    def getCurrentBranch(project):
        branches = RepoGit.exeCmdToGit(project, 'branch')
        if CmnUtils.isEmpty(branches): return ''
        bb = branches.split('\n')
        for b in bb:
            b = b.strip()
            if not b.startswith('*'): continue
            b = b[1:].strip()
            if b.startswith('(') or b.startswith('（'):  # (HEAD detached at tag-3.6.1)
                pos = b.rfind(' ')
                b = b[pos + 1:].strip()[:-1]
            return b
        return ''

    @staticmethod
    def hasBranch(project, branch):
        branches = RepoGit.exeCmdToGit(project, 'branch')
        if CmnUtils.isEmpty(branches): return False
        bb = branches.split('\n')
        for b in bb:
            b = b.strip()
            if b.startswith('*'): b = b[1:].strip()
            if branch == b: return True
        return False

    @staticmethod
    def fetchBranch(project, branch, force, ignoreFail, clean=False):
        if branch.startswith("refs/tags/"):  # fetch tag, "refs/tags/tag-3.6.3"
            return RepoGit.fetchTag(project, branch[10:], force, ignoreFail, clean)

        # LoggerUtils.println(project, branch, force, ignoreFail, clean)
        if not RepoGit.hasBranch(project, branch):
            ret = RepoGit.exeCmdToGit(project, 'fetch origin %s:%s' % (branch, branch))
            LoggerUtils.println(ret)
            if not RepoGit.hasBranch(project, branch):
                assert 0, 'Error: not found remote branch: ' + branch + ' for ' + project

        if force:
            ret = RepoGit.exeCmdToGit(project, 'clean -x -f -d')
            LoggerUtils.println(ret)

        frc = ' -f' if force else ''
        if RepoGit.hasBranch(project, branch):
            ret = RepoGit.exeCmdToGit(project, 'checkout%s %s' % (frc, branch))
        else:
            ret = RepoGit.exeCmdToGit(project, 'checkout%s -b %s origin/%s' % (frc, branch, branch))
        LoggerUtils.println(ret)

        currBranch = RepoGit.getCurrentBranch(project)
        if currBranch != branch:
            if ignoreFail: return False
            if clean: CmnUtils.remove(RepoEnv.getRootPath() + os.path.sep + project)
            assert 0, 'Error: ' + currBranch + ' != ' + branch + ' for ' + project

        RepoGit.gitSetUpstream(project, currBranch)

        ret = RepoGit.exeCmdToGit(project, 'pull origin %s' % (branch))
        return RepoGit.checkResult(ret)

    @staticmethod
    def fetchTag(project, tag, force, ignoreFail, clean=False):
        # LoggerUtils.println(project, branch, force, ignoreFail, clean)
        if RepoGit.getCurrentBranch(project) == tag: return True

        ret = RepoGit.exeCmdToGit(project, 'fetch origin %s' % (tag))
        LoggerUtils.println(ret)
        if None != ret and (0 <= ret.find('fatal') or 0 <= ret.find('error')):
            assert 0, 'Error: fetch tag fail, ' + tag + ' for ' + project

        ret = RepoGit.exeCmdToGit(project, 'checkout %s' % (tag))
        LoggerUtils.println(ret)
        if None != ret and (0 <= ret.find('fatal') or 0 <= ret.find('error')):
            assert 0, 'Error: checkout tag fail 1, ' + tag + ' for ' + project

        if RepoGit.getCurrentBranch(project) != tag:
            assert 0, 'Error: checkout tag fail 2, ' + tag + ' for ' + project
        return True

    @staticmethod
    def checkResult(ret):
        LoggerUtils.println(ret)
        if None == ret: return True
        lines = ret.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('error:'):
                assert 0, line
            if line.startswith('fatal:'):
                assert 0, line
        return True

    @staticmethod
    def updateCurrentBranch(project, dftBranch):
        branch = RepoGit.getCurrentBranch(project)
        if CmnUtils.isEmpty(branch): branch = dftBranch
        RepoGit.exeCmdToGit(project, 'pull origin ' + branch)

    @staticmethod
    def fetchGit(projectLocal, projectServer):
        localPath = RepoEnv.getRootPath() + os.sep + projectLocal
        projExist = os.path.isdir(localPath)
        if projExist:
            rname = RepoGit.getGitRemoteServerName(localPath)
            if rname == None or rname == projectServer: return projExist
            msg = 'file exist: ' + localPath
            msg += ', remote git changed: %s -> %s' % (rname, projectServer)
            msg += ', remove or backup, then try again'
            assert 0, msg

        sname = projectServer.split('/')[-1]
        if sname.endswith('.git'): sname = sname[:-4]
        tmpPath = RepoEnv.getRootPath() + os.sep + '.repo' + os.sep + FileUtils.getTempName('.tmp_')
        try:
            os.makedirs(tmpPath)
            CmnUtils.doCmd('cd %s && git clone %s/%s' % (tmpPath, RepoConfig.getGitRemoteHost(), projectServer))
            assert os.path.isdir(
                tmpPath + os.sep + sname + os.sep + '.git'), 'Make sure have correct access rights for ' + projectServer + ' !'

            pp = os.path.dirname(localPath)
            if not os.path.isdir(pp): os.makedirs(pp)
            shutil.move(tmpPath + os.sep + sname, localPath)
        except Exception as e:
            LoggerUtils.println(e)
            raise SyntaxError(e.message)
        finally:
            FileUtils.remove(tmpPath, True)
        return projExist

    @staticmethod
    def getGitRemoteServerName(path):
        s = CmnUtils.doCmd('cd %s && git remote -v' % (path))
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


if __name__ == "__main__":
    RepoEnv.init(sys.argv[1])
    RepoGit.exeCmdToGits(CmnUtils.joinArgs(sys.argv[2:]))
