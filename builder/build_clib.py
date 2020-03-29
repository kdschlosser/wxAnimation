
import os
import sys
import shutil
import build_framework
import distutils.log
from build_framework import build_clib as _build_clib


class build_clib(_build_clib.build_clib):
    user_options = [
        (
            'dep-version=',
            '',
            'Version of library to use, set to "dev" to use the master branch of the repo.'
        )
    ] + _build_clib.build_clib.user_options

    def initialize_options(self):
        module = sys.modules[self.__module__]
        self.url = getattr(module, 'URL')
        self.download_url = getattr(module, 'DOWNLOAD_URL')
        self.dep_version = getattr(module, 'VERSION')
        self.library_name = self.__class__.__name__.split('_')[-1]

    def finalize_options(self):
        build_clib.build_clib.finalize_options(self)
        self.build_temp = os.path.join(self.build_temp, self.library_name)

        build = self.distribution.get_command_obj('build')
        self.skip_build = getattr(build, 'no_' + self.library_name, False)

        if self.skip_build:
            return

        if not os.path.exists(self.build_clib):
            os.makedirs(self.build_clib)

        if not os.path.exists(self.build_temp):
            os.makedirs(self.build_temp)

    def run(self):
        if self.skip_build:
            distutils.log.info('Skipping {0} build.'.format(self.library_name))
            return

        if self.dep_version == 'dev':
            download_url = self.url + '/zipball/master'
        else:
            download_url = self.download_url.format(self.dep_version)

        if not build_framework.get_dep(os.path.join(self.build_temp, self.library_name), download_url):
            distutils.log.error('Failed to download {0} from "{1}"'.format(self.library_name, download_url))
            sys.exit(1)

        _build_clib.build_clib.run(self)
