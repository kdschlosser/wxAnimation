# -*- coding: utf-8 -*-

import sys
import os
import shutil
import distutils.log
from distutils.command.build import build as _build


class build(_build):

    user_options = [
        ('clean', None, 'clean'),
        ('dev', None, 'use development version')
    ] + _build.user_options

    boolean_options = ['clean', 'dev'] + _build.boolean_options

    def initialize_options(self):
        if 'DISTUTILS_DEBUG' in os.environ:
            distutils.log.set_threshold(distutils.log.DEBUG)

        _build.initialize_options(self)
        self.dev_repo = None
        self.clean = False
        self.dev = False

    def finalize_options(self):
        _build.finalize_options(self)
        # build_clib = self.distribution.get_command_obj('build_clib')
        # build_clib.ensure_finalized()

    def run(self):
        for sub_command in self.get_sub_commands():
            self.run_command(sub_command)
