# -*- coding: utf-8 -*-

from . import library_base


class Library(library_base.Library):

    def __init__(self, *args, **kwargs):
        library_base.Library.__init__(self, *args, **kwargs)
        self._ar_flags = ['rc']

    @property
    def prefix(self):
        return '/opt/local'

    @property
    def shared_lib_name(self):
        return self.name + '.so.' + self.version
