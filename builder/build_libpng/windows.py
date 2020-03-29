
from build_framework import PLATFORM
from ..sources import LIBPNG_SOURCES
from ..dep_versions import LIBPNG_VERSION
import build_framework.library.windows

MACROS = [
    ('_WINDOWS', ''),
    ('_CRT_SECURE_NO_DEPRECATE', ''),
    ('_CRT_SECURE_NO_WARNINGS', ''),
    ('_UNICODE', ''),
    ('UNICODE', ''),
    ('_WINDLL', ''),
    ('_USRDLL', '')
]

CFLAGS = [
    '/W4',
    '/WX',
    '/Yu"pngpriv.h"',
    '/wd"4996"',
    '/wd"4127"',
    '/fp:except-',
    '/Zc:wchar_t-',
    '/GS',
    '/TC',
    '/Ox',
    '/Zc:inline',
    '/Oy-',
]

INCLUDES = ['libpng', 'zlib']
UDEF_MACROS = []
LIB_DIRS = []
LIBS = ['zlib.lib']

LDFLAGS = [
    '/MANIFEST',
    '/LTCG:incremental',
    '/NXCOMPAT',
    '/IMPLIB:libpng.lib',
    '/VERSION:"16"',
    '/OPT:REF',
    '/INCREMENTAL:NO',
    '/MANIFESTUAC:"level=\'asInvoker\' uiAccess=\'false\'"',
    '/OPT:ICF',
    '/TLBID:1 '
]

EXTRA_OBJECTS = []

if PLATFORM == 'x86':
    LDFLAGS += ['/SAFESEH:NO']
else:
    LDFLAGS += ['/SAFESEH']


class Library(build_framework.library.windows.Library):

    def __init__(self):
        name = 'libpng'
        sources = LIBPNG_SOURCES
        include_dirs = INCLUDES
        define_macros = MACROS
        undef_macros = UDEF_MACROS
        library_dirs = LIB_DIRS
        libraries = LIBS
        runtime_library_dirs = ()
        extra_objects = EXTRA_OBJECTS
        extra_compile_args = CFLAGS
        extra_link_args = LDFLAGS
        export_symbols = ()
        depends = ()
        static_lib = True
        version = LIBPNG_VERSION

        build_framework.library.windows.Library.__init__(
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
            version=version,
        )

        # this enables the use of the build_framework multi threaded compiler
        self.build = self._build

