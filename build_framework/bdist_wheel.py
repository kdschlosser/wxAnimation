# -*- coding: utf-8 -*-

import os
import sys
import hashlib
import base64
import zipfile
import setuptools
import distutils.util
from distutils import log

PY3 = sys.version_info[0] >= 3


def get_file_hash(path, record, wheel_dir, install_dir=None):
    if install_dir is None:
        install_dir = path

    dirs = []

    for src in os.listdir(path):
        src = os.path.join(path, src)
        if (
                'EGG-INFO' in src or
                '__pycache__' in src or
                src.endswith('.pyc') or
                src.endswith('.pyo')
        ):
            continue

        if os.path.isdir(src):
            dirs += [src]
            continue

        sha256_hash = hashlib.sha256()
        # Read and update hash string value in blocks of 4K
        byte_count = 0
        pth = src.replace(install_dir, '')[1:]
        dst = os.path.join(wheel_dir, pth)

        dst_dir = os.path.split(dst)[0]

        if not os.path.exists(dst_dir):
            os.makedirs(dst_dir)

        dst = open(dst, 'wb')

        with open(src, "rb") as sha_f:
            for byte_block in iter(lambda: sha_f.read(4096), b""):
                sha256_hash.update(byte_block)
                byte_count += len(byte_block)
                dst.write(byte_block)

        if wheel_dir in src:
            src = src.replace(wheel_dir, '')[1:]
        if install_dir in src:
            src = src.replace(install_dir, '')[1:]

        add_sha(
            src,
            record,
            byte_count=byte_count,
            hex_digest=sha256_hash.hexdigest()
        )

        dst.close()

    for d in dirs:
        get_file_hash(d, record, wheel_dir, install_dir)


def add_sha(src, record, data=None, byte_count=None, hex_digest=None):
    if data is not None:
        if PY3:
            data = data.encode()

        byte_count = len(data)
        hex_digest = hashlib.sha256(data).hexdigest()

    if PY3:
        hex_digest = hex_digest.encode()

    sha_256 = base64.urlsafe_b64encode(hex_digest)

    if PY3:
        sha_256 = sha_256.decode()

    record.append(
        '{path},sha256={sha_256},{byte_count}'.format(
            path=src,
            sha_256=sha_256.replace('=', ''),
            byte_count=byte_count
        )
    )


class bdist_wheel(setuptools.Command):
    description = 'Create a wheel.'

    user_options = [
        ('bdist-dir=', None, 'temporary install path'),
        ('dev', None, '')
    ]

    boolean_options = ['dev']

    def initialize_options(self):
        self.bdist_dir = None
        self.dev = False

    def finalize_options(self):
        if self.bdist_dir is None:
            self.bdist_dir = os.path.join(
                'build',
                'lib.' + distutils.util.get_platform()
            )
            self.bdist_dir = os.path.abspath(self.bdist_dir)

        self.bdist_dir = self.bdist_dir.replace('"', '')
        install_options = dict(
            install_lib=('setup script', self.bdist_dir),
            dev=('setup script', self.dev)
        )
        self.distribution.command_options['install'] = install_options

    def run_install(self):
        self.run_command('install')

    def run(self):
        try:
            if not os.path.exists(self.bdist_dir):
                os.makedirs(self.bdist_dir)
        except:
            import traceback
            traceback.print_exc()
            raise

        dist_directory = os.path.join(self.bdist_dir, '..', '..', 'dist')
        dist_directory = os.path.abspath(dist_directory)
        if not os.path.exists(dist_directory):
            os.mkdir(dist_directory)

        self.run_install()

        log.info('Collecting wheel data.')

        for wheel_file in os.listdir(dist_directory):
            if wheel_file.endswith('egg'):
                break
        else:
            raise RuntimeError(
                'Unable to locate egg file to create wheel from.'
            )

        wheel_dir = os.path.join(self.bdist_dir, 'wheel')

        if not os.path.exists(wheel_dir):
            os.mkdir(wheel_dir)

        for f in os.listdir(self.bdist_dir):
            if f.startswith(self.distribution.metadata.name):
                install_dir = os.path.join(self.bdist_dir, f)

                dist_info = '{name}-{version}.dist-info'.format(
                    name=self.distribution.metadata.name,
                    version=self.distribution.metadata.version
                )

                dist_info = os.path.join(
                    wheel_dir,
                    dist_info
                )
                break
        else:
            raise RuntimeError(
                'Unable to locate module temporary installation.'
            )

        license_ = os.path.join(
            self.bdist_dir,
            '..',
            '..',
            'COPYRIGHT.txt'
        )

        egg_info_dir = os.path.join(install_dir, 'EGG-INFO')
        pkg_info = os.path.join(egg_info_dir, 'PKG-INFO')
        requires = os.path.join(egg_info_dir, 'requires.txt')
        top_level = os.path.join(egg_info_dir, 'top_level.txt')

        with open(pkg_info, 'r') as f:
            pkg_info = f.read()
        with open(requires, 'r') as f:
            requires = f.read()
        with open(top_level, 'r') as f:
            top_level = f.read()
        with open(license_, 'r') as f:
            license_ = f.read()

        pkg_info = pkg_info.rstrip()

        requires_dist = None
        for line in requires.split('\n'):
            if not line.strip():
                continue

            if line.startswith('['):
                requires_dist = line[2:-1]
            else:
                for oper in ('>=', '<=', '=='):
                    if oper in line:
                        line, ver = line.split(oper)
                        line += ' (' + oper + ver + ')'
                        break

                pkg_info += '\nRequires-Dist: ' + line
                if requires_dist is not None:
                    pkg_info += '; (' + requires_dist + ')'
                    requires_dist = None

        beg, description = pkg_info.split('Description: ')
        description, end = description.split('\n', 1)
        metadata = beg + end
        metadata += '\n\n' + description

        log.info('Creating wheel dist-info.')

        if wheel_dir in dist_info:
            sha_path = dist_info.replace(wheel_dir, '')[1:]
        else:
            sha_path = dist_info

        if install_dir in sha_path:
            sha_path = sha_path.replace(install_dir, '')[1:]

        if not os.path.exists(dist_info):
            os.mkdir(dist_info)

        with open(os.path.join(dist_info, 'top_level.txt'), 'w') as f:
            f.write(top_level)
        with open(os.path.join(dist_info, 'LICENSE'), 'w') as f:
            f.write(license_)
        with open(os.path.join(dist_info, 'METADATA'), 'w') as f:
            f.write(metadata)
        with open(os.path.join(dist_info, 'PKG-INFO'), 'w') as f:
            f.write(pkg_info)

        dist_records = []

        add_sha(
            os.path.join(sha_path, 'top_level.txt'),
            dist_records,
            top_level
        )
        add_sha(os.path.join(sha_path, 'PKG-INFO'), dist_records, pkg_info)
        add_sha(os.path.join(sha_path, 'LICENSE'), dist_records, license_)
        add_sha(os.path.join(sha_path, 'METADATA'), dist_records, metadata)

        entry_points = os.path.join(egg_info_dir, 'entry_points.txt')

        if os.path.exists(entry_points):
            with open(entry_points, 'r') as f:
                entry_points = f.read()

            with open(os.path.join(dist_info, 'entry_points.txt'), 'w') as f:
                f.write(entry_points)

            add_sha(
                os.path.join(sha_path, 'entry_points.txt'),
                dist_records,
                entry_points
            )

        wheel = (
            'Wheel-Version: 1.0\n'
            'Generator: bdist_wheel (0.33.1)\n'
            'Root-Is-Purelib: false\n'
        )

        platform_tag = (
            distutils.util.get_platform().replace('-', '_'.replace('.', '_'))
        )

        file_records = []

        log.info('Hashing wheel files.')
        get_file_hash(install_dir, file_records, wheel_dir)

        wheel_name = '{name}-{version}-{{0}}-none-{platform}.whl'.format(
            name=self.distribution.metadata.name,
            version=self.distribution.metadata.version,
            platform=platform_tag
        )

        def _write_wheel(*wheel_tags):
            with open(os.path.join(dist_info, 'WHEEL'), 'w') as fl:
                fl.write(wheel)
                for tag in wheel_tags:
                    fl.write('Tag: {0}-none-{1}\n'.format(tag, platform_tag))

            wheel_tags = '.'.join(wheel_tags)
            records = file_records[:]
            add_sha(os.path.join(sha_path, 'WHEEL'), records, wheel)

            records += dist_records[:]
            records += [os.path.join(sha_path, 'RECORD') + ',,']

            with open(os.path.join(dist_info, 'RECORD'), 'w') as fl:
                fl.write('\n'.join(records))

            wheel_path = os.path.join(
                dist_directory,
                wheel_name.format(wheel_tags)
            )

            log.info('Writing wheel file: ' + wheel_path)

            zip_file = zipfile.ZipFile(wheel_path, 'w', zipfile.ZIP_DEFLATED)
            for root, dirs, files in os.walk(wheel_dir):
                for fls in files:
                    fls = os.path.relpath(os.path.join(root, fls))
                    zip_file.write(fls)

            zip_file.close()

        cwd = os.getcwd()
        os.chdir(wheel_dir)

        ver = str(sys.version_info[0]) + str(sys.version_info[1])
        if ver in ('38', '37', '36', '35'):
            _write_wheel('cp38', 'cp37', 'cp36', 'cp35')
        elif ver in ('34', '33'):
            _write_wheel('cp34', 'cp33')
        elif ver in ('32', '31', '30'):
            _write_wheel('cp32', 'cp31', 'cp30')
        else:
            _write_wheel('cp27')

        os.chdir(cwd)
