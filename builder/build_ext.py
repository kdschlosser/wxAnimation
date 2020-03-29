
import os
from build_framework.build_ext import build_ext as _build_ext


class build_ext(_build_ext):

    def finalize_options(self):
        _build_ext.finalize_options(self)
        extensions = self.distribution.ext_modules

        for ext in extensions:
            ext.include_dirs = list(os.path.join(self.build_temp, item) for item in ext.include_dirs)
            ext.extra_objects = list(os.path.join(self.build_temp, item) for item in ext.extra_objects)

    def build_extension(self, ext):
        import cffi

        output = self.get_ext_fullpath(ext.name)

        libwebp = cffi.FFI()
        libwebp.set_source(
            output,
            open(ext.sources[0], 'r'),
            extra_objects=ext.extra_objects,
            libraries=ext.libraries,
            includes=ext.include_dirs,
            define_macros=ext.define_macros,
            library_dirs=[self.build_temp] + ext.library_dirs
        )

        libwebp.cdef(open(ext.header, 'r'))
        libwebp.compile(verbose=True)
