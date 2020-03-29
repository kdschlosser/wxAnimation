# -*- coding: utf-8 -*-

import os
from . import library_base


class Library(library_base.Library):

    @property
    def c_flags(self):
        c_flags = library_base.Library.c_flags.fget(self)

        command = [
            'test',
            '$(uname -U)',
            '-ge',
            '1002000;'
            'echo $?'
        ]

        from subprocess import Popen, PIPE

        p = Popen(command, stdout=PIPE, stderr=PIPE)

        if p.communicate()[0].strip() == '1':
            if not os.path.exists('/usr/local/include/iconv.h'):
                raise RuntimeError(
                    'FreeBSD pre 10.2: Please install libiconv from ports'
                )

            c_flags += '-I/usr/local/include'

        return c_flags
