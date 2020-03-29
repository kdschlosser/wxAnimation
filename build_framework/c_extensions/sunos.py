# -*- coding: utf-8 -*-

from __future__ import print_function
import os
from . import extension_base


class Extension(extension_base.Extension):

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
        if extra_compile_args is None:
            extra_compile_args = [
                '-g'
                '-Wmacro-redefined',
                '-Wdeprecated-declarations'
            ]

        extension_base.Extension.__init__(
            self,
            name,
            sources,
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
            swig_opts=swig_opts,
            depends=depends,
            language=language,
            optional=optional,
            **kw
        )
