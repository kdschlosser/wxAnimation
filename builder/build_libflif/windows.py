
from build_framework import PLATFORM
from ..sources import FLIF_SOURCES
from ..dep_versions import FLIF_VERSION
import build_framework.library.windows


MACROS = [
    ('FLIF_BUILD_DLL', ''),
    ('_CRT_SECURE_NO_WARNINGS', ''),
    ('FLIF_EXPORTS', ''),
    ('_WINDOWS', ''),
    ('_USRDLL', ''),
    ('_WINDLL', ''),
    ('_UNICODE', ''),
    ('UNICODE', '')

]

UDEF_MACROS = []

CFLAGS = [
    '/permissive-',
    '/W3',
    '/wd"4101"',
    '/wd"4244"',
    '/wd"4267"',
    '/Zc:wchar_t',
    '/Zc:inline',
    '/WX-',
]
LDFLAGS = [
    '/MANIFEST',
    '/LTCG:incremental',
    '/NXCOMPAT',
    '/IMPLIB:FLIF.lib',
    '/OPT:REF',
    '/INCREMENTAL:NO',
    '/SUBSYSTEM:WINDOWS',
    '/MANIFESTUAC:NO ',
    '/OPT:ICF',
    '/TLBID:1'
]

INCLUDES = [
    'libpng',
    'zlib',
    'flif/src',
    'flif/extern',
    'flif/src/image',
    'flif/src/library',
    'flif/src/maniac',
    'flif/src/transform'
]

LIBS = ['zlib.lib', 'libpng.lib']
LIB_DIRS = []
EXTRA_OBJECTS = []

if PLATFORM == 'x86':
    LDFLAGS += ['/SAFESEH:NO']
else:
    LDFLAGS += ['/SAFESEH']


class Library(build_framework.library.windows.Library):

    def __init__(self):
        name = 'libflif'
        sources = FLIF_SOURCES
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
        version = FLIF_VERSION

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

