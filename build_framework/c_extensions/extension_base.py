# -*- coding: utf-8 -*-

from __future__ import print_function
import os
import sys
import setuptools.extension


DEBUG_BUILD = os.path.splitext(sys.executable)[0].endswith('_d')


class Extension(setuptools.extension.Extension):
    # right now you use a dictionary in which you add the various information
    # to. and this is very hard to follow. in the end you then pass the
    # dictionary to the parent class of this class. You can trim down on the
    # hard to follow dictionary use and simply place the code that pertains
    # to a specific OS into a subclass of this class and just pass an instance
    # of that class directly to setup() this works pretty much the same as
    # the Library class. you would add a subclass of this class and a subclass
    # of the Library class to a file that is specific to that OS.

    def has_c_libraries(self):
        return False

    def __init__(
        self,
        name,
        sources,
        include_dirs=None,
        define_macros=None,
        undef_macros=None,
        library_dirs=None,
        libraries=None,
        runtime_library_dirs=None,
        extra_objects=None,
        extra_compile_args=None,
        extra_link_args=None,
        export_symbols=None,
        swig_opts=None,
        depends=None,
        language=None,
        optional=None,
        **kw  # To catch unknown keywords
    ):

        if DEBUG_BUILD:
            define_macros += [('_DEBUG', '')]

        if language is None:
            language = 'c++'

        setuptools.extension.Extension.__init__(
            self,
            name=name,
            language=language,
            extra_objects=extra_objects,
            sources=sources,
            include_dirs=include_dirs,
            define_macros=define_macros,
            libraries=libraries,
            extra_compile_args=extra_compile_args,
            extra_link_args=extra_link_args,
            undef_macros=undef_macros,
            library_dirs=library_dirs,
            runtime_library_dirs=runtime_library_dirs,
            export_symbols=export_symbols,
            swig_opts=swig_opts,
            depends=depends,
            optional=optional,
            **kw
        )

