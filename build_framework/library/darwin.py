# -*- coding: utf-8 -*-

from . import library_base
import os


class Library(library_base.Library):

    def __init__(self, *args, **kwargs):
        library_base.Library.__init__(self, *args, **kwargs)

        if self._cc is None:
            self._cc = 'clang'

        if self._cxx is None:
            self._cxx = 'clang++'

    @property
    def shared_lib_name(self):
        return '{0}-{0}.dylib'.format(self.name, self.version)

    @property
    def lib_name(self):
        return self.name + '.dylib'

    @property
    def t_arch(self):
        from subprocess import Popen, PIPE

        command = ['sw_vers', '-productVersion']
        p = Popen(command, stdout=PIPE, stderr=PIPE)
        darwin_version = p.communicate()[0].strip().decode('utf-8')
        mojave = float('.'.join(darwin_version.split('.')[:2])) >= 10.14

        if mojave:
            # Newer macOS releases don't support i386 so only build 64-bit
            target = ['-arch x86_64']
        else:
            target = ['-arch i386, -arch x86_64']

        return target
