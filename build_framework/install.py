# -*- coding: utf-8 -*-

from setuptools.command.install import install as _install


class install(_install):
    description = 'Install'

    user_options = [
        ('dev', None, 'use development version'),
        ('no-deps', 'N', "don't install dependencies"),
    ] + _install.user_options

    boolean_options = ['dev', 'no-deps'] + _install.boolean_options

    def initialize_options(self):
        self.no_deps = False
        self.dev = False
        _install.initialize_options(self)

    def finalize_options(self):
        build = self.distribution.get_command_obj('build')
        build.dev = self.dev
        _install.finalize_options(self)

    def run(self):
        # Explicit request for old-style install?  Just do it
        self.run_command('build_py')
        self.run_command('build')
        self.run_command('build_scripts')

        self.do_egg_install()
