# -*- coding: utf-8 -*-

from __future__ import print_function
import os
from . import extension_base


class Extension(extension_base.Extension):

    def __call__(self, build_ext):
        build_ext.distribution.has_c_libraries = self.has_c_libraries

        extension_base.Extension.__call__(self, build_ext)

        if self.static:
            self.libraries += ['udev', 'stdc++', 'resolv']
            self.extra_objects += []
            self.include_dirs += []
        else:
            self.libraries += []

        self.report_config()

    def __init__(self):
        include_dirs = []
        extra_objects = []
        libraries = []
        define_macros = []
        sources = []
        extra_compile_args = [
            '-g',
            '-Wmacro-redefined',
            '-Wdeprecated-declarations'
        ]

        extension_base.Extension.__init__(
            self,
            extra_objects=extra_objects,
            sources=sources,
            include_dirs=include_dirs,
            define_macros=define_macros,
            libraries=libraries,
            extra_compile_args=extra_compile_args
        )
