# -*- coding: utf-8 -*-

import os
from .. import build_clib
from ..dep_versions import WEBP_VERSION
from setuptools import Extension as _Extension


URL = 'https://storage.googleapis.com/downloads.webmproject.org/releases/webp'
DOWNLOAD_URL = URL + '/libwebp-{0}.tar.gz'
VERSION = WEBP_VERSION


# I know this seems kind of odd... I am doing a tiny bit of voodoo magic code here
# I need the class name in order to set up the directories
# and i use the __module__ attribute of the class in order to get this module instance
# from sys.modules. I use that module instance to grab the 3 constants in this file.
class build_libwebp(build_clib.build_clib):
    pass


class WebpExtension(_Extension):

    def __init__(self, *args, **kwargs):
        _Extension.__init__(self, *args, **kwargs)

        self.name = '_libwebp'
        self.sources = [os.path.join(os.path.dirname(__file__), 'extension.c')]
        self.header = os.path.join(os.path.dirname(__file__), 'extension.h')
        self.extra_objects = ['webpmux.lib', 'webpdemux.lib', 'webpdecoder.lib', 'webp.lib']
        self.include_dirs = [
            'webp/src/dec',
            'webp/src/demux',
            'webp/src/dsp',
            'webp/src/enc',
            'webp/src/mux',
            'webp/src/utils',
            'webp/src/webp'
        ]
        self.libraries = []








