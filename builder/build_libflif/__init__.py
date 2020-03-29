# -*- coding: utf-8 -*-

import os
from .. import build_clib
from ..dep_versions import FLIF_VERSION
from setuptools import Extension as _Extension

URL = 'https://github.com/FLIF-hub/FLIF'
DOWNLOAD_URL = URL + '/archive/v{0}.tar.gz'
VERSION = FLIF_VERSION


# I know this seems kind of odd... I am doing a tiny bit of voodoo magic code here
# I need the class name in order to set up the directories
# and i use the __module__ attribute of the class in order to get this module instance
# from sys.modules. I use that module instance to grab the 3 constants in this file.
class build_libflif(build_clib.build_clib):
    pass


class FLIFExtension(_Extension):

    def __init__(self, *args, **kwargs):
        _Extension.__init__(self, *args, **kwargs)

        self.name = '_libflif'
        self.sources = [os.path.join(os.path.dirname(__file__), 'extension.c')]
        self.header = os.path.join(os.path.dirname(__file__), 'extension.h')
        self.extra_objects = ['flif.lib']
        self.libraries = ['flif']
        self.include_dirs = [
            'libflif/src',
            'libflif/src/library',
            'libflif/src/maniac',
            'libflif/src/transform',
            'libflif/src/image',
            'libflif/extern',
        ]