# -*- coding: utf-8 -*-

from __future__ import print_function
import os
import sys
from . import extension_base
from ..msvc import environment


DEBUG_BUILD = os.path.splitext(sys.executable)[0].endswith('_d')


class Extension(extension_base.Extension):

    def __call__(self, build_ext):
        extension_base.Extension.__call__(self, build_ext)

        if self.static:
            # this is a really goofy thing to have to do. But distutils will
            # pitch a fit if we try to run the linker without a PyInit
            # expression. it does absolutely nothing. Decoration I guess.
            build_clib = build_ext.distribution.get_command_obj('build_clib')

            self.extra_objects += []

            self.include_dirs += [
                build_clib.build_clib
            ]

        else:
            self.libraries += []
            self.extra_compile_args += []

        self.extra_link_args += []
        self.report_config()

    def __init__(self):
        extra_objects = []
        define_macros = []
        sources = []
        include_dirs = []

        libraries = []
        extra_compile_args = [
            '/FS',
            # Enables function-level linking.
            '/Gy',
            # Creates fast code.
            '/O2',
            # Uses the __cdecl calling convention (x86 only).
            '/Gd',
            # Omits frame pointer (x86 only).
            '/Oy',
            # Generates intrinsic functions.
            '/Oi',
            # Specify floating-point behavior.
            '/Zi',
            '/Ox',
            '/fp:precise',
            # Specifies standard behavior
            '/Zc:wchar_t',
            # Specifies standard behavior
            '/Zc:forScope',
            # I cannot remember what this does. I do know it does get rid of
            # a compiler warning
            '/EHsc',
            # compiler warnings to ignore
            '/wd4996',
            '/wd4244',
            '/wd4005',
            '/wd4800',
            '/wd4351',
            '/wd4273'
        ]

        if environment.visual_c.version > 10.0:
            # these compiler flags are not valid on
            # Visual C++ version 10.0 and older

            extra_compile_args += [
                # Forces writes to the program database (PDB) file to be
                # serialized through MSPDBSRV.EXE.
                '/FS',
                # Specifies standard behavior
                '/Zc:inline'
            ]

        if DEBUG_BUILD:
            define_macros += [('_DEBUG', 1)]
            libraries += []
        else:
            libraries += []

        libraries += [environment.python.dependency.split('.')[0]]

        extension_base.Extension.__init__(
            self,
            extra_objects=extra_objects,
            sources=sources,
            include_dirs=include_dirs,
            define_macros=define_macros,
            libraries=libraries,
            extra_compile_args=extra_compile_args,
        )
