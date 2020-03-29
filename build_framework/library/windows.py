# -*- coding: utf-8 -*-

import distutils.log
import os
import sys
import threading
import shutil

from . import library_base
from ..msvc import environment


# this is an easy macro to tell if a debugging version of python is what is
# running if it is what is running then we want to build a debugging version
# of the clib. the use of this will allow you to set any preprocessor
# macros to build a debugging version of the clib
DEBUG_BUILD = os.path.splitext(sys.executable)[0].endswith('_d')


# in order to have distutils handle the building of the clib there has to be
# a call to PyInit so we create a cpp file and place the call in it. The call
# actually does nothing except allow everything to get build.
DLL_MAIN = '''

void PyInit_{LIBRARY_NAME}() {{}}

'''


class Library(library_base.Library):

    @property
    def include_dirs(self):
        return self._include_dirs

    @property
    def undef_macros(self):
        return ['/U "' + macro + '"' for macro in self._undef_macros]

    @property
    def define_macros(self):
        macros = []

        for macro, value in self._define_macros:
            if not value == '':
                macros += ['/D "' + macro + '"']
            else:
                macros += ['/D "' + macro + '=' + repr(value) + '"']
        return macros

    @property
    def c_flags(self):
        c_flags = self._c_flags

        for arg in self._extra_compile_args:
            if arg.startswith('--'):
                if arg[2:] in c_flags:
                    c_flags.remove(arg[2:])
            elif arg not in c_flags:
                c_flags += [arg]

        del self._extra_compile_args[:]
        return c_flags

    def _compile_c(self, c_file, build_clib):
        temp_path = build_clib.build_temp
        object_file = os.path.split(c_file)[-1]
        object_file = os.path.join(
            os.path.abspath(temp_path),
            os.path.splitext(object_file)[0] + '.obj'
        )

        if os.path.exists(object_file):
            return

        command = ['cl.exe']
        command += self.c_flags
        command += self.define_macros
        command += self.undef_macros
        command += ['/I"' + os.path.join(build_clib.build_temp, inc) + '"' for inc in self.include_dirs]

        if DEBUG_BUILD:
            pdb_file = os.path.join(os.path.split(object_file)[0], self.lib_name + '.pdb')
            command += ['/Fd"' + pdb_file + '"']
        command += ['/Fa"' + os.path.split(object_file)[0] + '"']

        command += ['/Tc"' + c_file + '"']
        command += ['/Fo"' + object_file + '"']

        for item in self._c_flags:
            if item.startswith('/Yu'):
                command += ['/Fp "' + os.path.join(os.path.split(object_file)[0], self.name + '.pch') + '"']
                break

        build_clib.spawn(command, cwd=build_clib.build_temp)

        return object_file

    def _compile_cpp(self, cpp_file, build_clib):
        temp_path = build_clib.build_temp

        object_file = os.path.split(cpp_file)[-1]
        object_file = os.path.join(
            os.path.abspath(temp_path),
            os.path.splitext(object_file)[0] + '.obj'
        )

        if os.path.exists(object_file):
            return

        command = ['cl.exe']
        command += self.c_flags
        command += self.define_macros
        command += self.undef_macros
        command += self.include_dirs
        if DEBUG_BUILD:
            pdb_file = os.path.join(os.path.split(object_file)[0], self.lib_name + '.pdb')
            command += ['/Fd"' + pdb_file + '"']
        command += ['/Tp"' + cpp_file + '"']
        command += ['/Fo"' + object_file + '"']

        for item in self._c_flags:
            if item.startswith('/Yu'):
                command += ['/Fp "' + os.path.join(os.path.split(object_file)[0], self.name + '.pch') + '"']
                break

        build_clib.spawn(command, cwd=build_clib.build_temp)

        return object_file

    def __init__(
        self,
        name,
        sources,
        include_dirs=(),
        define_macros=(),
        undef_macros=(),
        library_dirs=(),
        libraries=(),
        runtime_library_dirs=(),
        extra_objects=(),
        extra_compile_args=(),
        extra_link_args=(),
        export_symbols=(),
        depends=(),
        static_lib=True,
        version='',
    ):
        library_base.Library.__init__(
            self,
            name=name,
            sources=sources,
            include_dirs=include_dirs,
            define_macros=define_macros,
            undef_macros=undef_macros,
            library_dirs=library_dirs,
            libraries=libraries,
            runtime_library_dirs=runtime_library_dirs,
            extra_objects=extra_objects,
            extra_compile_args=extra_compile_args,
            extra_link_args=extra_link_args,
            export_symbols=export_symbols,
            depends=depends,
            static_lib=static_lib,
            version=version
        )

        self._c_flags = [
            '/GL',
            '/Gy',
            '/Gm-',
            '/O2',
            '/errorReport:prompt',
            '/Zc:forScope',
            '/Gd',
            '/Oi',
            '/FC',
            '/EHsc',
            '/GF',
            '/nologo',
        ]

        self._ld_flags = [
            '/NOLOGO'
            '/VERBOSE',
            '/SUBSYSTEM:WINDOWS'
        ]

        define_macros = self._define_macros

        if DEBUG_BUILD:
            self._c_flags += ['/Od', '/Zi']

            if not self._static_lib:
                self._c_flags += ['/MDd']

            if ('_DEBUG', '') not in define_macros:
                define_macros += [[('_DEBUG', '')]]

            self._ld_flags += ['/DEBUG']

        else:
            if not self._static_lib:
                self._c_flags += ['/MD']

            if ('NDEBUG', '') not in define_macros:
                define_macros += [('NDEBUG', '')]

        if environment.platform == 'x64':
            if ('WIN64', '') not in define_macros:
                define_macros += [('WIN64', '')]
            if ('_WIN64', '') not in define_macros:
                define_macros += [('_WIN64', '')]

            self._c_flags += [
                '/fp:precise'
            ]
            self._ld_flags += ['/MACHINE:X64']
        else:

            if ('WIN32', '') not in define_macros:
                define_macros += [('WIN32', '')]
            if ('_WIN32', '') not in define_macros:
                define_macros += [('_WIN32', '')]

            self._ld_flags += ['/MACHINE:X86']

        if static_lib:
            self._ld_flags += ['/LIB']
        else:
            self._ld_flags += ['/DLL']

            if ('_DLL', '') not in define_macros:
                define_macros += [('_DLL', '')]

        if environment.visual_c.version > 10.0:
            # these compiler flags are not valid on
            # Visual C++ version 10.0 and older

            self._c_flags += [
                # Forces writes to the program database (PDB) file to be
                # serialized through MSPDBSRV.EXE.
                '/FS',
                # Specifies standard behavior
                '/Zc:inline'
            ]

        self.files_to_compile = {}

        self._cc = 'cl.exe'
        self._cxx = 'cl.exe'
        self._ar = 'lib.exe'
        self._ld = 'link.exe'
        self._ranlib = None

    @property
    def library_dirs(self):
        return ['/LIBPATH"' + lib_path + '"' for lib_path in self._library_dirs]

    @property
    def ld_flags(self):
        ld_flags = self._ld_flags

        for arg in self._extra_link_args:
            if arg.startswith('--'):
                if arg[2:] in ld_flags:
                    ld_flags.remove(arg[2:])
            else:
                ld_flags += [arg]

        del self._extra_link_args[:]

        return ld_flags

    def link(self, objects, build_clib):
        if not objects:
            return

        lib_file = os.path.join(build_clib.build_clib, self.lib_name)
        if os.path.exists(lib_file):
            return

        command = [self.ld] + self.ld_flags
        command += ['/OUT:"' + lib_file + '"']
        command += ['/LIBPATH:"' + build_clib.build_clib + '"']
        command += self.library_dirs

        if DEBUG_BUILD:
            command += ['/PDB:"' + os.path.splitext(lib_file)[0] + '.pdb"']

        if '/MANIFEST' in command:
            command += ['/ManifestFile:"' + lib_file + '.intermediate.manifest"']

        for library in self.libraries:
            command += ['"' + library + '"']

        for item in command[:]:
            if item.startswith('/PGD') or item.startswith('/IMPLIB'):
                command.remove(item)
                item, pth = item.split(':', 1)

                if not os.path.split(pth)[0]:
                    pth = os.path.join(build_clib.build_clib, item)

                command += ['/{0}:"{1}"'.format(item, pth)]

        command += objects
        build_clib.spawn(command)

