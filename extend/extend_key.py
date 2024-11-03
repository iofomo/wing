#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @brief: signature for target file
# @date:  2023.05.16 14:40:50

import os
import sys

g_this_file = os.path.realpath(sys.argv[0])
g_this_path = os.path.dirname(g_this_file)
sys.path.append(os.path.dirname(g_this_path))

from utils.utils_cmn import CmnUtils
from utils.utils_cipher import CipherUtils
from utils.utils_logger import LoggerUtils
from utils.utils_file import FileUtils
from utils.utils_import import ImportUtils
from utils.utils_zip import ZipUtils
from basic.arguments import BasicArgumentsValue

g_wing_path = ImportUtils.initEnv(os.path.dirname(g_this_path))


# --------------------------------------------------------------------------------------------------------------------------
def doExportMobileProvision(tempPath, f):
    FileUtils.ensureDir(tempPath)

    global g_mp_file
    g_mp_file = None

    def doCallback(fullName, fileName):
        global g_mp_file
        if None != g_mp_file: return -1
        if fileName.endswith('embedded.mobileprovision'):
            g_mp_file = fullName
            return 1
        return 0

    ZipUtils.unzip2(f, tempPath, doCallback)
    return g_mp_file


def doList(envPath, f, pwd):
    if CmnUtils.isEmpty(f):
        LoggerUtils.error('Fail, not found file')
        return

    if CmnUtils.isRelativePath(f): f = envPath + os.sep + f
    # print(f)
    if f.endswith('.apk'):  # "wing -key list com.demo.apk"
        ret = CmnUtils.doCmd('keytool -list -printcert -jarfile ' + CmnUtils.formatCmdArg(f))
        LoggerUtils.println(ret)
        return
    if f.endswith('.ipa'):  # "wing -key list com.demo.ipa"
        tempPath = envPath + "/.cache/" + FileUtils.getTempName()
        try:
            mpf = doExportMobileProvision(tempPath, f)
            # print(mpf)
            ret = CmnUtils.doCmd('security cms -D -i ' + CmnUtils.formatCmdArg(mpf))
            LoggerUtils.println(ret)
        except Exception as e:
            LoggerUtils.exception(e)
        finally:
            FileUtils.remove(tempPath, True)
        return
    if f.endswith('.mobileprovision'):  # # "wing -key list embedded.mobileprovision"
        ret = CmnUtils.doCmd('security cms -D -i ' + CmnUtils.formatCmdArg(f))
        LoggerUtils.println(ret)
        return
    if f.endswith('.RSA') or f.endswith('.rsa'):  # "wing -key list cert.RSA"
        ret = CmnUtils.doCmd('keytool -printcert -file ' + CmnUtils.formatCmdArg(f))
        LoggerUtils.println(ret)
        return
    if f.endswith('.keystore') or f.endswith('.jks'):  # "wing -key list demo.keystore"
        if CmnUtils.isEmpty(pwd):
            ret = CmnUtils.doCmd('keytool -list -v -keystore ' + CmnUtils.formatCmdArg(f))
        else:
            ret = CmnUtils.doCmd(('keytool -list -v -storepass %s -keystore ' % (pwd)) + CmnUtils.formatCmdArg(f))
        LoggerUtils.println(ret)
        return
    LoggerUtils.error('UNsupport key list: ' + f)


def doCreate(envPath, _type, _mode):
    if 'rsa' == _type.lower():
        # openssl genrsa -out private.pem 2048
        # openssl rsa -in private.pem -pubout -out public.pem
        prvtFile = envPath + os.sep + FileUtils.getTempTimeName('private_', '.pem')
        mode = '2048' if CmnUtils.isEmpty(_mode) else _mode
        succ = CmnUtils.doCmdCall('openssl genrsa -out %s %s' % (prvtFile, mode))
        assert succ and os.path.isfile(prvtFile), 'openssl genrsa fail'

        pubFile = envPath + os.sep + FileUtils.getTempTimeName('public_', '.pem')
        succ = CmnUtils.doCmdCall('openssl rsa -in %s -pubout -out %s' % (prvtFile, pubFile))
        assert succ and os.path.isfile(prvtFile), 'openssl rsa fail'
        LoggerUtils.light('>>> ' + prvtFile[len(envPath) + 1:])
        LoggerUtils.light('>>> ' + pubFile[len(envPath) + 1:])
        return
    LoggerUtils.error('UNsupport key create: ' + ('none' if CmnUtils.isEmpty(_type) else _type) + ', ' + ('none' if CmnUtils.isEmpty(_mode) else _mode))


def doHash(str):
    h, f = CmnUtils.getHash(str)

    LoggerUtils.println('md5: ' + CipherUtils.md5String(str))
    LoggerUtils.println('sha256: ' + CipherUtils.sha256String(str))

    LoggerUtils.println('unique for long: 0x%x' % ((h << 32) | f))
    LoggerUtils.println('hash: 0x%x, flag: 0x%x' % (h, f))
    LoggerUtils.println('{ 0x%x, 0x%x }, // %s' % (h, f, str))


def showHelp():
    help = '''
        -key {type}
            create {key type} {mode}
                create RSA public and private keys with 1024 or 2048(default) mode
            list {file} [pwd]
                print key/sign information for apk/ipa/mobileprovision/keystore/jks/rsa/... file
            hash {string}
                print md5/sha256/hash/... of string
    '''
    LoggerUtils.println(' ')
    LoggerUtils.println(help)


def run():
    '''
    wing -key
    '''
    argv = BasicArgumentsValue()
    envPath, spacePath, cmd = argv.get(0), argv.get(1), argv.get(2)

    # "wing -key list ${file} ${pwd}"
    if cmd == 'list': return doList(envPath, argv.get(3), argv.get(4))
    # "wing -key create ${type} ${mode}"
    if cmd == 'create': return doCreate(envPath, argv.get(3), argv.get(4))
    # "wing -key hash ${string}"
    if cmd == 'hash': return doHash(argv.get(3))

    showHelp()


if __name__ == "__main__":
    run()
