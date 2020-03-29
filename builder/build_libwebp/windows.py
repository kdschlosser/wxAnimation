
from build_framework import PLATFORM
from ..sources import WEBP_DECODER_SOURCES, WEBP_SOURCES, WEBP_MUX_SOURCES, WEBP_DEMUX_SOURCES
from ..dep_versions import WEBP_VERSION

import build_framework.library.windows

MACROS = [
    ('_CRT_SECURE_NO_WARNINGS', ''),
    ('_UNICODE', ''),
    ('UNICODE', ''),
    ('WIN32_LEAN_AND_MEAN', ''),
    ('HAVE_WINCODEC_H', ''),
    ('WEBP_USE_THREAD', '')
]

LIBS = ['zlib.lib', 'libpng']
LIB_DIRS = []
UDEF_MACROS = []
CFLAGS = ['/nologo', '/O2', '/MT', '/W3']
LDFLAGS = ['/LARGEADDRESSAWARE', '/MANIFEST', '/NXCOMPAT', '/DYNAMICBASE']

INCLUDES = [
    'webp/src/dec',
    'webp/src/demux',
    'webp/src/dsp',
    'webp/src/enc',
    'webp/src/mux',
    'webp/src/utils',
    'webp/src/webp',
    'libpng',
    'zlib'
]

if PLATFORM == 'x64':
    LDFLAGS += ['/SAFESEH:NO']
else:
    LDFLAGS += ['/SAFESEH']


class WebPDecoderLibrary(build_framework.library.windows.Library):

    def __init__(self):
        name = 'libwebpdecoder'
        sources = WEBP_DECODER_SOURCES
        include_dirs = INCLUDES
        define_macros = MACROS
        undef_macros = UDEF_MACROS
        library_dirs = LIB_DIRS
        libraries = LIBS
        runtime_library_dirs = ()
        extra_objects = ()
        extra_compile_args = CFLAGS
        extra_link_args = LDFLAGS
        export_symbols = ()
        depends = ()
        static_lib = True
        version = WEBP_VERSION

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


class WebPLibrary(build_framework.library.windows.Library):

    def __init__(self):
        name = 'libwebp'
        sources = WEBP_SOURCES
        include_dirs = INCLUDES
        define_macros = MACROS
        undef_macros = UDEF_MACROS
        library_dirs = LIB_DIRS
        libraries = LIBS
        runtime_library_dirs = ()
        extra_objects = ()
        extra_compile_args = CFLAGS
        extra_link_args = LDFLAGS
        export_symbols = ()
        depends = ()
        static_lib = True
        version = WEBP_VERSION

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


class WebPMuxLibrary(build_framework.library.windows.Library):

    def __init__(self):
        name = 'libwebpmux'
        sources = WEBP_MUX_SOURCES
        include_dirs = INCLUDES
        define_macros = MACROS
        undef_macros = UDEF_MACROS
        library_dirs = LIB_DIRS
        libraries = LIBS
        runtime_library_dirs = ()
        extra_objects = ()
        extra_compile_args = CFLAGS
        extra_link_args = LDFLAGS
        export_symbols = ()
        depends = ()
        static_lib = True
        version = WEBP_VERSION

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


class WebPDemuxLibrary(build_framework.library.windows.Library):

    def __init__(self):
        name = 'libwebpdemux'
        sources = WEBP_DEMUX_SOURCES
        include_dirs = INCLUDES
        define_macros = MACROS
        undef_macros = UDEF_MACROS
        library_dirs = LIB_DIRS
        libraries = LIBS
        runtime_library_dirs = ()
        extra_objects = ()
        extra_compile_args = CFLAGS
        extra_link_args = LDFLAGS
        export_symbols = ()
        depends = ()
        static_lib = True
        version = WEBP_VERSION

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
