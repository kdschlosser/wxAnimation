# -*- coding: utf-8 -*-

from .. import build_clib
from ..dep_versions import LIBPNG_VERSION
import os
import shutil


URL = 'https://github.com/glennrp/libpng'
DOWNLOAD_URL = URL + 'archive/v{0}.tar.gz'
VERSION = LIBPNG_VERSION


# I know this seems kind of odd... I am doing a tiny bit of voodoo magic code here
# I need the class name in order to set up the directories
# and i use the __module__ attribute of the class in order to get this module instance
# from sys.modules. I use that module instance to grab the 3 constants in this file.
class build_libpng(build_clib.build_clib):

    def finalize_options(self):
        build_clib.build_clib.finalize_options(self)
        src = os.path.join(self.build_temp, 'libpng/scripts/pnglibconf.h.prebuilt')
        dst = os.path.join(self.build_temp, 'libpng/pnglibconf.h')
        shutil.copyfile(src, dst)
