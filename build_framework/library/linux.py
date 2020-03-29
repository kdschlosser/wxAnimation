# -*- coding: utf-8 -*-

from . import library_base
import sys
import os


class Library(library_base.Library):

    @property
    def shared_lib_name(self):
        return self.name + '.so.' + self.version
