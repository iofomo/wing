#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @brief:  load resource
# @date:   2023.05.10 14:40:50

import os
import sys

from utils.utils_cmn import CmnUtils
from utils.utils_import import ImportUtils

# ----------------------------------------------------------------------------------------------------------------------
class Resource:
    sRes = None

    @classmethod
    def __do_init__(cls):
        cls.sRes = {}
        f = ImportUtils.getProjectPath() + '/res/res-' + CmnUtils.getLanguageName() + '.txt'
        with open(f, 'rb') as f:
            while True:
                line = f.readline().decode()
                if CmnUtils.isEmpty(line): break
                pos = line.find('=')
                if pos <= 0: continue
                k = line[:pos].strip()
                if CmnUtils.isEmpty(k): continue
                v = line[pos + 1:].strip()
                if len(v) < 2: continue
                cls.sRes[k] = v[1:-1]
        # print(cls.sRes)

    @classmethod
    def getString(cls, typ):
        if None == cls.sRes: cls.__do_init__()
        k = '%d' % typ
        return cls.sRes[k] if k in cls.sRes else ''

# if __name__ == "__main__":
#    Resource.getString(0)
