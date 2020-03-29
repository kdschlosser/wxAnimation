# -*- coding: utf-8 -*-

import distutils
import distutils.errors
import distutils.core
import distutils.command.build_clib
import distutils.log
from distutils.sysconfig import customize_compiler
import distutils.dir_util
import os

from . import spawn_process

from .library.library_base import Library


class build_clib(distutils.core.Command):
    user_options = [
        ('build-clib=', 'b',
         "directory to build C/C++ libraries to"),
        ('build-temp=', 't',
         "directory to put temporary build by-products"),
        ('debug', 'g',
         "compile with debugging information"),
        ('force', 'f',
         "forcibly build everything (ignore file timestamps)"),
    ]

    boolean_options = ['debug', 'force']

    help_options = [
        ('help-compiler', None,
         "list available compilers", distutils.command.build_clib.show_compilers),
    ]

    def spawn(self, *args, **kwargs):
        spawn_process.spawn(*args, **kwargs)

    # we override the compilers mkpath so we can inject the verbose option.
    # the compilers version does not allow for setting of a verbose level
    # and distutils.dir_util.mkpath defaults to a verbose level of 1 which
    # which prints out each and every directory it makes. This congests the
    # output unnecessarily.
    def mkpath(self, name, mode=0o777):
        distutils.dir_util.mkpath(
            name,
            mode,
            dry_run=self.compiler.dry_run,
            verbose=0
        )

    def initialize_options(self):
        self.build_clib = None
        self.build_temp = None

        # List of libraries to build
        self.libraries = None

        # Compilation options for all libraries
        self.include_dirs = None
        self.define = None
        self.undef = None
        self.debug = None
        self.force = 0
        self.compiler = None

    def finalize_options(self):
        # This might be confusing: both build-clib and build-temp default
        # to build-temp as defined by the "build" command.  This is because
        # I think that C libraries are really just temporary build
        # by-products, at least from the point of view of building Python
        # extensions -- but I want to keep my options open.

        self.set_undefined_options(
            'build',
            ('build_temp', 'build_clib'),
            ('build_temp', 'build_temp'),
            ('compiler', 'compiler'),
            ('debug', 'debug'),
            ('force', 'force')
        )

        if not os.path.exists(self.build_clib):
            os.makedirs(self.build_clib)

        if not os.path.exists(self.build_temp):
            os.makedirs(self.build_temp)

        self.libraries = self.distribution.libraries
        self.check_library_list(self.libraries)

        if self.include_dirs is None:
            self.include_dirs = self.distribution.include_dirs or []
        if isinstance(self.include_dirs, str):
            self.include_dirs = self.include_dirs.split(os.pathsep)

    def run(self):
        if not self.libraries:
            return

        # we are leaving this here so if wanted the built in compiler for distutils can be used
        # Instead of using a tuple and a dict to provide compiler options I decided to make a class
        # call Library. This class is what will hold all of the various build components needed
        # for a build. Now. There is a method "build" that ghets called. if this method is overridden
        # it is what gets used instread of the internal compiler. I created a wrapper class around the
        # Library which institutes a multi threaded compiling process. we no longer use the built in
        # compiler with distutils. I am not able to use the distutils compiler in a threaded scenario
        # because it was not designed to be thread safe and things get all kinds of funky.

        from distutils.ccompiler import new_compiler
        self.compiler = new_compiler(
            compiler=self.compiler,
            dry_run=self.dry_run,
            force=self.force
        )

        # replace the compilers spawn and mkpath with the onces that we have written

        self.compiler.spawn = self.spawn
        self.compiler.mkpath = self.mkpath

        customize_compiler(self.compiler)

        if self.include_dirs is not None:
            self.compiler.set_include_dirs(self.include_dirs)
        if self.define is not None:
            # 'define' option is a list of (name,value) tuples
            for (name, value) in self.define:
                self.compiler.define_macro(name, value)

        if self.undef is not None:
            for macro in self.undef:
                self.compiler.undefine_macro(macro)

        self.build_libraries(self.libraries)

    def check_library_list(self, libraries):
        if not isinstance(libraries, (list, tuple)):
            raise distutils.errors.DistutilsSetupError(
                  "'libraries' options need to be either a list or a tuple.")

        for lib in libraries:
            if not isinstance(lib, Library):
                raise distutils.errors.DistutilsSetupError(
                    "contents of 'libraries' needs to be instances of 'Library'  not " + str(type(lib))
                )

            # lib.validate()

    def get_library_names(self):
        # Assume the library list is valid -- 'check_library_list()' is
        # called from 'finalize_options()', so it should be!
        if not self.libraries:
            return None

        lib_names = []
        for lib in self.libraries:
            lib_names.append(lib.name)
        return lib_names

    def get_source_files(self):
        self.check_library_list(self.libraries)
        filenames = []

        for lib in self.libraries:
            filenames.extend(lib.sources)

        return filenames

    def build_libraries(self, libraries):

        for lib in libraries:
            distutils.log.info("building '%s' library", lib.name)
            try:
                lib.build(self)
            except NotImplementedError:
                # First, compile the source code to object files in the library
                # directory.  (This should probably change to putting object
                # files in a temporary build directory.)
                include_dirs = lib.include_dirs

                objects = self.compiler.compile(
                    lib.sources,
                    output_dir=self.build_temp,
                    macros=lib.macros,
                    include_dirs=include_dirs,
                    debug=self.debug
                )

                # Now "link" the object files together into a static library.
                # (On Unix at least, this isn't really linking -- it just
                # builds an archive.  Whatever.)
                self.compiler.create_static_lib(
                    objects,
                    lib.name,
                    output_dir=self.build_clib,
                    debug=self.debug
                )
