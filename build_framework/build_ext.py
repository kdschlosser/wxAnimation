# -*- coding: utf-8 -*-

import sys
from setuptools.command.build_ext import build_ext as _build_ext
import distutils.log
import os
import shutil

PY3 = sys.version_info[0] > 2


class build_ext(_build_ext):

    def initialize_options(self):
        self.static = False
        self.saved_libtype = _build_ext.libtype
        self.saved_use_stubs = _build_ext.use_stubs

        _build_ext.initialize_options(self)

    def finalize_options(self):
        build = self.distribution.get_command_obj('build')
        build.ensure_finalized()

        if self.static:
            self.link_shared_object = self.static_object
            _build_ext.libtype = 'static'
            _build_ext.use_stubs = False
        else:
            self.link_shared_object = self.shared_object
            _build_ext.libtype = 'shared'
            _build_ext.use_stubs = True

    def run(self):
        distutils.log.info('\n')
        for ext in self.distribution.extensions:
            self.build_extension(ext)

        distutils.log.info('\n')

        # TODO: write code parser for building a stub file
        # a stub file is used to provide a "peek" inside of an en extension. This is what allows
        # an IDE to provide type hinting and intellisense.
        # Python 2.x does not have support for .pyi files. But I know a way to provide the same
        # ability without the need to use a .pyi file.

        # self.run_command('build_stub')

    def get_ext_fullpath(self, name):
        # this method is overridden because of Windows and needing to compile an extension with the same
        # version compiler that was used to compile Python. When building a wheel or an egg
        # we are able to create that binary for each of the Python versions that use a specific msvc compiler
        # an example would be 3.5, 3.6, 3.7, 3.8  all use msvc 14. because the naming conventions of the pyd file
        # target specific python versions like this "kiwisolver.cp37-win_amd64.pyd" we need to shop out all
        # of the middle bits to end up with "kiwisolver.pyd". this file name for the extension is still able
        # to be loaded by python. and this is what gets packaged into the wheel. so we are able to build
        # 4 wheels or 4 eggs with only having to run the build for one of the python versions listed above.
        # the wheel/egg filename is what is going to set the python version/archeticture the wheel/egg is
        # allowed to be installed on.

        path = _build_ext.get_ext_fullpath(
            self,
            name
        )

        path, file_name = os.path.split(path)

        '_libflif.cp38.cp37.cp36.cp35-win_amd64.pyd'

        tag = 'cp' + str(sys.version_info[0]) + str(sys.version_info[1])

        if tag[2:] in ('38', '37', '36', '35'):
            name = name.replace(tag, 'cp38.cp37.cp36.cp35')
        elif tag[2:] in ('34', '33'):
            name = name.replace(tag, 'cp34.cp33')
        elif tag[2:] in ('32', '31', '30'):
            name = name.replace(tag, 'cp32.cp31.cp30')

        return os.path.join(path, file_name)

    def build_extension(self, ext):
        ext_path = self.get_ext_fullpath(ext.name)
        pdb_file = os.path.splitext(ext_path)[0] + '.pdb'

        try:
            delattr(self, 'link_shared_object')
            _build_ext.libtype = self.saved_libtype
            _build_ext.use_stubs = self.saved_use_stubs
        except AttributeError:
            pass

        if 'bdist_wheel' in sys.argv:
            if not os.path.exists(ext_path):
                _build_ext.build_extension(self, ext)
                distutils.log.info('\n')
        else:
            _build_ext.build_extension(self, ext)
            distutils.log.info('\n')

        if not sys.platform.startswith('win'):
            from subprocess import Popen, PIPE

            proc = Popen(['objcopy', '--only-keep-debug', ext_path, pdb_file], stdout=PIPE, stderr=PIPE)
            proc.communicate()

            proc = Popen(['objcopy', '--strip-debug', ext_path], stdout=PIPE, stderr=PIPE)
            proc.communicate()

            proc = Popen(['objcopy', '--add-gnu-debuglink', pdb_file, ext_path], stdout=PIPE, stderr=PIPE)
            proc.communicate()

    def shared_object(
        self,
        objects,
        output_libname,
        output_dir=None,
        libraries=None,
        library_dirs=None,
        runtime_library_dirs=None,
        export_symbols=None,
        debug=0,
        extra_preargs=None,
        extra_postargs=None,
        build_temp=None,
        target_lang=None
    ):
        self.link(
            self.SHARED_LIBRARY,
            objects,
            output_libname,
            output_dir,
            libraries,
            library_dirs,
            runtime_library_dirs,
            export_symbols,
            debug,
            extra_preargs,
            extra_postargs,
            build_temp,
            target_lang
        )

    def static_object(
        self,
        objects,
        output_libname,
        output_dir=None,
        libraries=None,
        library_dirs=None,
        runtime_library_dirs=None,
        export_symbols=None,
        debug=0,
        extra_preargs=None,
        extra_postargs=None,
        build_temp=None,
        target_lang=None
    ):
        # XXX we need to either disallow these attrs on Library instances,
        # or warn/abort here if set, or something...
        # libraries=None, library_dirs=None, runtime_library_dirs=None,
        # export_symbols=None, extra_preargs=None, extra_postargs=None,
        # build_temp=None

        assert output_dir is None  # distutils build_ext doesn't pass this
        output_dir, filename = os.path.split(output_libname)
        basename, ext = os.path.splitext(filename)
        if self.library_filename("x").startswith('lib'):
            # strip 'lib' prefix; this is kludgy if some platform uses
            # a different prefix
            basename = basename[3:]

        self.create_static_lib(
            objects,
            basename,
            output_dir,
            debug,
            target_lang
        )
