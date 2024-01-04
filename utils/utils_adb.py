#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @brief:  adb shell am ..., such as
#          adb shell am start ...
#          adb shell am startservice ...
#          adb shell broadcast ...
#          adb shell content call ...
# @date:   2023.08.10 14:40:50

import sys, os

from utils.utils_import import ImportUtils
from utils.utils_cmn import CmnUtils
from utils.utils_file import FileUtils
from utils.utils_net import NetUtils
from utils.utils_zip import ZipUtils
from utils.utils_logger import LoggerUtils

ImportUtils.initEnv()

BASE_URL_FMT = 'http://www.iofomo.com/download/adb/adb-%s'
# --------------------------------------------------------------------------------------------------------------------------
class AdbUtils:

    g_adb_env_status = 0

    @staticmethod
    def getFileName():
        if CmnUtils.isOsWindows(): return 'win-x64.zip'
        if CmnUtils.isOsMac(): return 'mac-x64.dmg'
        return 'linux-x64.zip'

    @staticmethod
    def ensureEnv():
        if AdbUtils.isADBActive(): return
        binFile = AdbUtils.getAdbBinFile()

        # download
        LoggerUtils.println('download adb ...')
        url = BASE_URL_FMT % AdbUtils.getFileName()
        try:
            zPath = ImportUtils.getProjectPath() + '/plugin'
            if not os.path.exists(zPath): os.makedirs(zPath)
            zFile = zPath + os.sep + AdbUtils.getFileName()
            NetUtils.downloadFileWithProgress(url, zFile)
            LoggerUtils.println('download success')
        except Exception as e:
            print(e)
            return None

        ZipUtils.unzip(zFile, os.path.dirname(binFile))
        if os.path.isfile(binFile): return binFile
        LoggerUtils.e('invalid adb file')
        return None

    @classmethod
    def doAdbCmd(cls, cmd):
        if not AdbUtils.isADBActive(): return ''
        if 1 < cls.g_adb_env_status:
            adbFile = AdbUtils.getAdbBinFile()
            return CmnUtils.doCmd(('%s ' % adbFile) + cmd)
        return CmnUtils.doCmd('adb ' + cmd)

    @classmethod
    def isADBActive(cls):
        if 0 == cls.g_adb_env_status:
            ret, err = CmnUtils.doCmdEx('adb --version')
            if not CmnUtils.isEmpty(ret) and 0 <= ret.find('Version'):
                cls.g_adb_env_status = 1
            elif os.path.isfile(AdbUtils.getAdbBinFile()):
                cls.g_adb_env_status = 2
        return 0 < cls.g_adb_env_status

    @staticmethod
    def getAdbBinFile():
        return ImportUtils.getProjectPath() + '/plugin/adb/adb' + CmnUtils.getOsStuffix()

    @staticmethod
    def getFileTimestamp(f):
        cmd = 'shell date +%s -r "' + f + '"'
        try:
            ret = AdbUtils.doAdbCmd(cmd)
            if None == ret: return 0
            LoggerUtils.println(ret)
            ret = ret.strip()
            if len(ret) <= 0 or not ret.isdigit(): return 0
            return int(ret)
        except Exception as e:
            LoggerUtils.println(e)
        return 0

    @staticmethod
    def getDevices():
        ret = AdbUtils.doAdbCmd('devices')
        items = ret.split('\n')

        devices = []
        for item in items:
            item = item.strip()
            if CmnUtils.isEmpty(item) or not item.endswith('device'): continue
            devices.append(item.split('\t')[0])
        return devices

    @staticmethod
    def isDeviceConnected(): return 0 < len(AdbUtils.getDevices())

    @staticmethod
    def pull(src, des):
        des1 = os.path.abspath(des)
        ts1 = ts2 = 0
        if os.path.exists(des1): ts1 = FileUtils.getModifyTime(des1)
        des2 = des1 + os.sep + os.path.basename(src)
        if os.path.exists(des2): ts2 = FileUtils.getModifyTime(des2)

        AdbUtils.doAdbCmd('pull "%s" "%s"' % (src, des1))
        tsNew = FileUtils.getModifyTime(des1)
        if 0 != tsNew and ts1 < tsNew: return True
        tsNew = FileUtils.getModifyTime(des2)
        if 0 != tsNew and ts2 < tsNew: return True
        return False

    @staticmethod
    def push(src, des):
        src = os.path.abspath(src)
        ts1 = AdbUtils.getFileTimestamp(des)
        des2 = des + os.sep + os.path.basename(src)
        ts2 = AdbUtils.getFileTimestamp(des2)

        AdbUtils.doAdbCmd('push "%s" "%s"' % (src, des))
        tsNew = AdbUtils.getFileTimestamp(des)
        if 0 != tsNew and ts1 <= tsNew: return True
        tsNew = AdbUtils.getFileTimestamp(des2)
        if 0 != tsNew and ts2 <= tsNew: return True
        return False

    @staticmethod
    def stop(pkg):
        print('stop: ' + pkg)
        ret = AdbUtils.doAdbCmd('shell am force-stop %s' % pkg)
        print(ret)

    @staticmethod
    def clear(pkg):
        print('clear: ' + pkg)
        ret = AdbUtils.doAdbCmd('shell pm clear %s' % pkg)
        print(ret)

    @staticmethod
    def getApkFile(pkgName):
        while True:
            ret = AdbUtils.doAdbCmd('shell pm path %s' % pkgName)
            if None != ret:
                ret = ret.strip().split('\n')[0]
                if ret.startswith('package:') and ret.endswith('apk'):
                    return ret[len('package:'):]
            ret = AdbUtils.doAdbCmd('shell pm path --user 0 %s' % pkgName)
            if None != ret:
                ret = ret.strip().split('\n')[0]
                if ret.startswith('package:') and ret.endswith('apk'):
                    return ret[len('package:'):]
            return None

    @staticmethod
    def isInstalled(pkgName):
        if AdbUtils.getApkFile(pkgName): return True
        apps = AdbUtils.getInstallApps()
        if None == apps: return False
        return pkgName in apps

    @staticmethod
    def install(apkFile):
        ret = AdbUtils.doAdbCmd('install -r "%s"' % apkFile)
        if None == ret: return False
        return 0 <= ret.lower().find('success')

    @staticmethod
    def uninstall(pkgName):
        ins = AdbUtils.isInstalled(pkgName)
        ret = AdbUtils.doAdbCmd('uninstall "%s"' % pkgName)
        if None == ret: return not ins
        return 0 <= ret.lower().find('success') or not ins

    @staticmethod
    def getInstallAppsWithSystem():
        apps = set()
        if AdbUtils.__getInstallApps__(apps, 'shell pm list packages -s'): return apps
        return None

    @staticmethod
    def getInstallAppsWithThird():
        apps = set()
        if AdbUtils.__getInstallApps__(apps, 'shell pm list packages -3'): return apps
        return None

    @staticmethod
    def getInstallAppsWithDisable():
        apps = set()
        if AdbUtils.__getInstallApps__(apps, 'shell pm list packages -d'): return apps
        return None

    @staticmethod
    def getInstallAppsWithEnable():
        apps = set()
        if AdbUtils.__getInstallApps__(apps, 'shell pm list packages -e'): return apps
        return None

    @staticmethod
    def getInstallApps():
        apps = set()
        if not AdbUtils.__getInstallApps__(apps, 'shell pm list packages -e'): return None
        if not AdbUtils.__getInstallApps__(apps, 'shell pm list packages -d'): return None
        return apps

    @staticmethod
    def __getInstallApps__(apps, cmd):
        ret = AdbUtils.doAdbCmd(cmd)
        if CmnUtils.isEmpty(ret): return True

        items = ret.split("\n")
        for item in items:
            item = item.strip()
            if len(item) <= 0: continue
            pos = item.find(":")
            if 0 < pos: item = item[pos + 1:]
            if 'android' == item: continue
            apps.add(item)
        return True

    @staticmethod
    def startActivity(pkgName, activityName, tName, tVal, args):
        """
        launch target app with activity
        :param pkgName:
        :param activityName:
        :param tName:
        :param tVal:
        :param args:
        :return:
        """
        atype = ' --ei %s %d' % (tName, tVal)
        astring = ''
        for k, v in args.items():
            astring += ' --es %s %s' % (k, v)
        cmd = 'shell am start -n %s/%s%s%s' % (pkgName, activityName, atype, astring)
        return AdbUtils.doAdbCmd(cmd)

    @staticmethod
    def startService(pkgName, serviceName, tName, tVal, args):
        atype = ' --ei %s %d' % (tName, tVal)
        astring = ''
        for k, v in args.items():
            astring += ' --es %s %s' % (k, v)
        cmd = 'shell am startservice -n %s/%s%s%s' % (pkgName, serviceName, atype, astring)
        return AdbUtils.doAdbCmd(cmd)

    @staticmethod
    def sendBroadcast(action, tName, tVal, args):
        atype = ' --ei %s %d' % (tName, tVal)
        astring = ''
        for k, v in args.items():
            astring += ' --es %s %s' % (k, v)
        cmd = 'shell am broadcast -a %s%s%s' % (action, atype, astring)
        return AdbUtils.doAdbCmd(cmd)

    # @staticmethod
    # def sendBroadcast(pkgName, action, tName, tVal, args):
    #     atype = ' --ei %s %d' % (tName, tVal)
    #     astring = ''
    #     for k,v in args.items():
    #         astring += ' --es %s %s' % (k, v)
    #     cmd = 'shell am broadcast -a %s/%s%s%s' % (pkgName, action, atype, astring)
    #     return AdbUtils.doAdbCmd(cmd)

    @staticmethod
    def callProvider(authorities, tName, tVal, args):
        astring = ''
        for k, v in args.items():
            astring += ' --extra %s:s:%s' % (k, v)
        cmd = 'shell content call --uri content://%s --method abg --extra %s:i:%d%s' % (authorities, tName, tVal, astring)
        return AdbUtils.doAdbCmd(cmd)

    @staticmethod
    def startInstrument(pkgName, args=None):
        ret = AdbUtils.doAdbCmd('shell pm list instrumentation')
        if None == ret:
            LoggerUtils.println('Not found instrument !')
            return -1

        target = None
        items = ret.split('\n')
        for item in items:
            item = item.strip()
            if item.startswith('instrumentation:'): item = item[len('instrumentation:'):]
            pos = item.find('(')
            if 0 < pos: item = item[:pos].strip()
            if not item.startswith(pkgName + '/'): continue
            target = item
            break
        if None == target:
            assert -2, 'Not found instrument for: ' + pkgName

        astring = ''
        if None != args:
            for k, v in args.items(): astring += ' -e %s %s' % (k, v)
        cmd = 'shell am instrument -w %s %s' % (target, astring)
        return AdbUtils.doAdbCmd(cmd)

    @staticmethod
    def __get_value__(line, key):
        key += '='
        items = line.split(' ')
        for item in items:
            if not item.startswith(key): continue
            return item[len(key):]
        return None

    @staticmethod
    def dumpActivity():
        """
          Stack #0: type=home mode=fullscreen
              isSleeping=false
              mBounds=Rect(0, 0 - 0, 0)
    
                Task id #1
                mBounds=Rect(0, 0 - 0, 0)
                mMinWidth=-1
                mMinHeight=-1
                mLastNonFullscreenBounds=null
                * TaskRecord{6950f7b #1 A=com.huawei.android.launcher U=0 StackId=0 sz=1}
                  userId=0 effectiveUid=u0a89 mCallingUid=u0a158 mUserSetupComplete=true mCallingPackage=com.tencent.mm
                  affinity=com.huawei.android.launcher
                  intent={act=android.intent.action.MAIN cat=[android.intent.category.HOME] flg=0x10000300 cmp=com.huawei.android.launcher/.unihome.UniHomeLauncher}
                  mActivityComponent=com.huawei.android.launcher/.unihome.UniHomeLauncher
                  autoRemoveRecents=false isPersistable=true numFullscreen=1 activityType=2
                  rootWasReset=false mNeverRelinquishIdentity=true mReuseTask=false mLockTaskAuth=LOCK_TASK_AUTH_PINNABLE
                  Activities=[ActivityRecord{6a3b344 u0 com.huawei.android.launcher/.unihome.UniHomeLauncher t1}]
                  askedCompatMode=false inRecents=true isAvailable=true
                  mRootProcess=ProcessRecord{6925171 2492:com.huawei.android.launcher/u0a89}
                  stackId=0
                  hasBeenVisible=true mResizeMode=RESIZE_MODE_RESIZEABLE mSupportsPictureInPicture=false isResizeable=true lastActiveTime=1927917742 (inactive for 2s)
                    Hist #0: ActivityRecord{6a3b344 u0 com.huawei.android.launcher/.unihome.UniHomeLauncher t1}
                      Intent { act=android.intent.action.MAIN cat=[android.intent.category.HOME] flg=0x10000300 cmp=com.huawei.android.launcher/.unihome.UniHomeLauncher }
                      ProcessRecord{6925171 2492:com.huawei.android.launcher/u0a89}
    
                Running activities (most recent first):
                  TaskRecord{6950f7b #1 A=com.huawei.android.launcher U=0 StackId=0 sz=1}
                    Run #0: ActivityRecord{6a3b344 u0 com.huawei.android.launcher/.unihome.UniHomeLauncher t1}
        """
        activities = {}
        ret = AdbUtils.doAdbCmd('shell dumpsys activity')
        if ret.startswith('error:') or len(ret) < 256:
            LoggerUtils.w(ret)
            return activities

        status = 0
        lines = ret.split('\n')
        for line in lines:
            line = line.strip()
            if len(line) <= 0: continue
            if line.startswith('ACTIVITY MANAGER ACTIVITIES'):
                status = 1
                continue  # start
            if line.startswith('Task id #') or line.startswith('* Task{'):
                if 1 != status: break
                status = 2
                continue
            if line.startswith('Hist #') and 2 == status:
                status = 3
                continue
            if 3 == status:
                if line.startswith('Intent'):
                    '''
                    Intent { act=android.intent.action.MAIN cat=[android.intent.category.HOME] flg=0x10000300 cmp=com.huawei.android.launcher/.unihome.UniHomeLauncher }
                    '''
                    val = AdbUtils.__get_value__(line, 'cmp')
                    if None == val: continue
                    pkg, act = val.split('/')
                    if pkg not in activities: activities[pkg] = line
                elif line.startswith('ProcessRecord'):
                    '''
                    ProcessRecord{6925171 2492:com.huawei.android.launcher/u0a89}
                    '''
                    pos = line.find(':')
                    line = line[pos + 1:]
                    pos = line.find('/')
                    pkg = line[:pos]
                    if pkg not in activities: activities[pkg] = line
        return activities

    @staticmethod
    def isTopPackageActivity(pkg, activity=None):
        activities = AdbUtils.dumpActivity()
        if pkg not in activities: return False
        # Intent { flg=0x10000000 cmp=com.demo/com.demo.MainActivity (has extras) }
        return None == activity or 0 < activities.get(pkg).find('/' + activity + ' ')

    @staticmethod
    def isTopPackageWindow(pkg):
        return pkg in AdbUtils.dumpWindow()

    @staticmethod
    def dumpWindow():
        """
          Window #7 Window{37172e1 u0 com.demo}:
            mDisplayId=0 stackId=0 mSession=Session{39faa2d 23185:u0a10339} mClient=android.os.BinderProxy@3a79ab5
            mOwnerUid=10339 mShowToOwnerOnly=true package=com.demo appop=SYSTEM_ALERT_WINDOW
            mAttrs={(960,1112)(wrapxwrap) gr=TOP START CENTER sim={adjust=pan} ty=APPLICATION_OVERLAY hwFlags=#0 isEmuiStyle=0 statusBarColor=#0 navigationBarColor=#0 fmt=TRANSPARENT
              fl=NOT_FOCUSABLE NOT_TOUCH_MODAL SHOW_WHEN_LOCKED HARDWARE_ACCELERATED}
            Requested w=150 h=150 mLayoutSeq=4042
            mHasSurface=true isReadyForDisplay()=true mWindowRemovalAllowed=false
            WindowStateAnimator{39c8bc9 }:
              Surface: shown=true layer=0 alpha=1.0 rect=(0.0,0.0) 150 x 150 transform=(1.0, 0.0, 1.0, 0.0)
              mTmpSize=[0,0][150,150]
            mForceSeamlesslyRotate=false seamlesslyRotate: pending=null finishedFrameNumber=0
            isOnScreen=true
            isVisible=true
            canReceiveKeys=false
            hwNotchSupport=false
            mEnforceSizeCompat=false
            mInvGlobalScale=1.0
            mGlobalScale=1.0
          Window #1 Window{ba053be u0 com.demo/com.demo.ui.LauncherUI}:
            mDisplayId=0 stackId=1 mSession=Session{1524e71 31164:u0a10113} mClient=android.os.BinderProxy@7e61a79
            mOwnerUid=10113 mShowToOwnerOnly=true package=com.demo appop=NONE
            mAttrs=WM.LayoutParams{(0,0)(fillxfill) sim=#132 ty=1 fl=#81810100 extfl=#0 blurRatio=1.0 blurMode=0 fmt=-3 wanim=0x7f1101c4 vsysui=0x2700 needsMenuKey=2}
            Requested w=720 h=1280 mLayoutSeq=962
            mHasSurface=false mShownFrame=[0.0,0.0][720.0,1280.0] isReadyForDisplay()=false
            WindowStateAnimator{3f081e9 com.demo/com.demo.ui.LauncherUI}:
              mShownAlpha=1.0 mAlpha=1.0 mLastAlpha=0.0
        """
        windows = set()
        ret = AdbUtils.doAdbCmd('shell dumpsys window')
        # print(ret)
        if ret.startswith('error:'):
            LoggerUtils.w(ret)
            return windows

        pkg = None
        status = 0
        lines = ret.split('\n')
        for line in lines:
            line = line.strip()
            if len(line) <= 0:
                if 0 < status: break  # end
                continue
            if line.startswith('WINDOW MANAGER WINDOWS'):
                status = 1
                continue  # start
            if status <= 0: continue
            if line.startswith('Window #'):
                pkg = None
                status = 2
                continue
            if status <= 1: continue

            val = AdbUtils.__get_value__(line, 'package')
            if not CmnUtils.isEmpty(val): pkg = val
            display = AdbUtils.__get_value__(line, 'isReadyForDisplay()')
            if None != display:
                if 'true' == display and None != pkg and pkg not in ['android', 'com.android.systemui']:
                    windows.add(pkg)
                status = 1
                continue
        return windows

    @staticmethod
    def printlnDump():
        activities = AdbUtils.dumpActivity()
        windows = AdbUtils.dumpWindow()
        if 0 < len(windows):
            LoggerUtils.println('Top Window: ')
            for app in windows: LoggerUtils.println('\tpackage: ' + app)
        if 0 < len(activities):
            LoggerUtils.println('Top Activity: ')
            for pkg, line in activities.items(): LoggerUtils.println('\tpackage: ' + pkg + ', ' + line)


def run():
    pass
    # print(AdbUtils.getDevices())
    # apps = AdbShell.getInstallAppsWithSystem()
    # for app in apps: print(app)
    # print('-----------------------------------')
    # apps = AdbShell.getInstallAppsWithThird()
    # for app in apps: print(app)
    # print('-----------------------------------')
    # apps = AdbShell.getInstallApps()
    # for app in apps: print(app)
    # print('-----------------------------------')


if __name__ == "__main__":
    run()
