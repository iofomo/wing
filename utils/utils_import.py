#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @brief:  utils for zip/unzip file
# @date:   2023.08.10 14:40:50

import sys, os


class ImportUtils:

    @staticmethod
    def initEnv():
        try:
            if sys.version_info.major < 3:  # 2.x
                reload(sys)
                sys.setdefaultencoding('utf8')
            elif 3 == sys.version_info.major and sys.version_info.minor <= 3:  # 3.0 ~ 3.3
                import imp
                imp.reload(sys)
            else:  # 3.4 <=
                import importlib
                importlib.reload(sys)
            import _locale
            _locale._getdefaultlocale = (lambda *args: ['en_US', 'utf8'])
        except Exception as e:
            pass
        wingPath = os.path.expanduser("~") + os.sep + '.wing/wing' #  such as: /Users/${username}/.wing/wing
        return wingPath
