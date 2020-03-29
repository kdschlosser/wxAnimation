# -*- coding: utf-8 -*-
import os
import shutil
import distutils.log
import subprocess
import sys
import threading
import shutil
import distutils.errors

from .. import spawn_process


def parse_flags(env_param):
    if env_param in os.environ:
        flags = os.environ[env_param]
    else:
        flags = ''

    out_flags = []
    single_quote_count = 0
    double_quote_count = 0

    last_char = ''
    for char in list(flags):
        if char == '"':
            if last_char == '\\':
                continue

            if double_quote_count:
                double_quote_count -= 1
            else:
                double_quote_count += 1

        elif char == "'":
            if last_char == '\\':
                continue
            if single_quote_count:
                single_quote_count -= 1
            else:
                single_quote_count += 1
        elif (
            char == ' ' and
            not single_quote_count and
            not double_quote_count
        ):
            out_flags += ['']
            continue

        out_flags[len(out_flags) - 1] += char

    return out_flags


def get_sources(src_path, ignore):
    found = []
    for src_f in os.listdir(src_path):
        src = os.path.join(src_path, src_f)
        if os.path.isdir(src):
            if src_f.lower() in ignore:
                continue

            found += get_sources(src, ignore)
        elif src_f.endswith('.c') or src_f.endswith('.cpp'):
            found += [src]
    return found


class Library(object):

    def __init__(
        self,
        name,
        sources,
        version,
        include_dirs=(),
        define_macros=(),
        undef_macros=(),
        library_dirs=(),
        libraries=(),
        runtime_library_dirs=(),
        extra_objects=(),
        extra_compile_args=(),
        extra_link_args=(),
        export_symbols=(),
        depends=(),
        static_lib=True,
    ):

        if not isinstance(sources, (list, tuple)):
            try:
                sources = list(s.strip() for s in sources.split(','))
            except:
                raise distutils.errors.DistutilsArgError(
                    'Sources supplied to a Library need to be a list, tuple or comma seperated string'
                )

        self.name = name
        self._sources = list(sources)
        self._include_dirs = list(include_dirs)
        self._define_macros = list(define_macros)
        self._undef_macros = list(undef_macros)
        self._library_dirs = list(library_dirs)
        self._libraries = list(libraries)
        self._runtime_library_dirs = list(runtime_library_dirs)
        self._extra_objects = list(extra_objects)
        self._extra_compile_args = list(extra_compile_args)
        self._extra_link_args = list(extra_link_args)
        self._export_symbols = list(export_symbols)
        self._depends = list(depends)
        self._static_lib = static_lib
        self.version = version

        self._cc = os.environ.get('CC', None)
        self._cxx = os.environ.get('CXX', None)
        self._ar = os.environ.get('AR', 'ar')
        self._ld = os.environ.get('LD', 'ld')
        self._ranlib = os.environ.get('RANLIB', 'ranlib')
        self._ar_flags = ['rc']
        self._c_flags = parse_flags('CFLAGS')
        self._cpp_flags = parse_flags('CPPFLAGS')
        self._ld_flags = parse_flags('LDFLAGS')
        self._running_threads = {}

    @property
    def library_dirs(self):
        return self._library_dirs

    @property
    def sources(self):
        return self._sources

    @property
    def prefix(self):
        if sys.platform.startswith('win'):
            return ''
        else:
            return os.path.join('/usr', 'local')

    @property
    def sys_config_path(self):
        if sys.platform.startswith('win'):
            return ''
        else:
            return os.path.join(self.prefix, 'etc')

    @property
    def pkg_config_path(self):
        if sys.platform.startswith('win'):
            return ''
        else:
            if os.path.exists('/usr/lib64'):
                return os.path.join('/usr', 'lib64', 'pkgconfig')
            else:
                return os.path.join('/usr', 'lib', 'pkgconfig')

    @property
    def lib_inst_path(self):
        if sys.platform.startswith('win'):
            return ''
        else:
            if os.path.exists('/usr/lib64'):
                path = 'lib64'
            else:
                path = 'lib'

            path += '.' + self.machine
            if self._static_lib:
                return path
            else:
                return os.path.join(self.prefix, path)

    @property
    def machine(self):
        if sys.platform.startswith('win'):
            if sys.maxsize ** 32 > 64:
                return 'x64'
            else:
                return 'x86'

        else:
            if sys.maxsize ** 32 > 64:
                return 'x86_64'
            else:
                return 'i686'

    @property
    def t_arch(self):
        return []

    @property
    def ar(self):
        return self._ar

    @property
    def ar_flags(self):
        return self._ar_flags

    @property
    def ld_flags(self):
        return self._ld_flags

    @property
    def ld(self):
        return self._ld

    @property
    def lib_name(self):
        if sys.platform.startswith('win'):
            if self._static_lib:
                return self.name + '.lib'
            else:
                return self.name + '.dll'
        else:
            if self._static_lib:
                return self.name + '.a'
            else:
                return self.name + '.so'

    @property
    def ranlib(self):
        return self._ranlib

    @property
    def cc(self):
        return self._cc

    @property
    def cxx(self):
        return self._cxx

    @property
    def c_flags(self):
        return self._c_flags

    @property
    def cpp_flags(self):
        return self._cpp_flags

    @property
    def libraries(self):
        return self._libraries

    @libraries.setter
    def libraries(self, _):
        pass

    @property
    def include_dirs(self):
        return ['-I' + include for include in self._include_dirs]

    @include_dirs.setter
    def include_dirs(self, _):
        pass

    @property
    def so_path(self):
        if sys.platform.startswith('win'):
            return

        from .. import pkgconfig

        ldpath = pkgconfig.libs_only_l(self.name)[2:]

        distutils.log.info(
            "Running ldconfig on {0}... be patient ...".format(ldpath)
        )

        return ldpath

    def link(self, objects, build_clib):
        build_path = build_clib.build_clib
        lib_path = os.path.join(build_path, self.lib_name)

        if os.path.exists(lib_path):
            return

        if self._static_lib:
            with spawn_process.print_lock:
                sys.stdout.write('linking static library...\n')
                sys.stdout.flush()

            command = [self.ar] + self.ar_flags + [lib_path] + objects
            build_clib.spawn(command)

            command = [self.ranlib, lib_path]
            build_clib.spawn(command)

        else:
            with spawn_process.print_lock:
                sys.stdout.write('linking shared library...\n')
                sys.stdout.flush()

            command = [self.ld] + self.ld_flags + self.t_arch
            command += ['-o', self.shared_lib_name]
            command += objects + self.libraries
            build_clib.spawn(command)

            command = ['ln', '-sf', self.shared_lib_name, lib_path]
            build_clib.spawn(command)
            build_clib.spawn(['ldconfig', self.so_path], cwd=build_path)

    def build_pkg_config_file(self, build_clib):
        if sys.platform.startswith('win'):
            return

        checked_paths = []

        pc = self.name + 'pc'
        pc_in = self.name + '.pc.in'

        for src in self.sources:
            path = os.path.dirname(src)

            if not path:
                path = os.getcwd()

            if path not in checked_paths:
                files = os.listdir(path)
                if pc_in in files and pc in files:
                    pc = os.path.join(path, pc)
                    pc_in = os.path.join(path, pc_in)
                    break
        else:
            raise RuntimeError('Unable to locate ' + repr(pc) + ' and ' + repr(pc_in))

        with spawn_process.print_lock:
            sys.stdout.write('building pkg-config file...\n')
            sys.stdout.flush()

        exec_prefix = os.path.join('/usr', 'local', 'bin')

        command = [
            "sed "
            "-e 's|[@]prefix@|{prefix}|g' "
            "-e 's|[@]exec_prefix@|{exec_prefix}|g' "
            "-e 's|[@]libdir@|{libdir}|g' "
            "-e 's|[@]includedir@|{includedir}/|g' "
            "-e 's|[@]sysconfdir@|{sysconfdir}/|g' "
            "-e 's|[@]gitversion@|{gitversion}|g' "
            "-e 's|[@]VERSION@|{version}|g' "
            "-e 's|[@]LIBS@|{libs}|g' "
            "< \"{pc_in}\" "
            "> \"{pc}\"".format(
                prefix=self.prefix,
                exec_prefix=exec_prefix,
                libdir=self.lib_inst_path,
                includedir=self.include_path,
                sysconfdir=self.sys_config_path,
                gitversion=self.version,
                version=self.version,
                libs=' '.join(lib.lstrip('-').lstrip('l ') for lib in self.libraries),
                pc_in=pc_in,
                pc=pc
            )
        ]

        build_clib.spawn(command)

    @property
    def shared_lib_name(self):
        return '{0}-{0}.so'.format(self.name, self.version)

    def clean(self, build_clib):
        build_path = os.path.join(build_clib.build_clib, self.name)
        temp_path = os.path.join(build_clib.build_temp, self.name)

        if os.path.exists(build_path):
            distutils.log.info("Cleaning {0} ... be patient ...".format(build_path))
            try:
                shutil.rmtree(build_path)
            except OSError:
                pass

        if temp_path != build_path and os.path.exists(temp_path):
            distutils.log.info("Cleaning {0} ... be patient ...".format(temp_path))
            try:
                shutil.rmtree(temp_path)
            except OSError:
                pass

    def _compile_c(self, c_file, build_clib):
        temp_path = os.path.join(build_clib.build_temp, self.name)

        with spawn_process.print_lock:
            sys.stdout.write(
                'compiling ' + os.path.split(c_file)[-1] + '...\n'
            )
            sys.stdout.flush()

        c_file = os.path.abspath(c_file)
        file_name = os.path.splitext(os.path.split(c_file)[-1])[0]
        d_file = os.path.join(temp_path, file_name + '.d')
        tmp_file = d_file + '.tmp'
        o_file = os.path.join(temp_path, file_name + '.o')

        command = [self.cc]
        command += self.c_flags
        command += self.include_dirs
        command += ['{0} > {1}'.format(c_file, d_file)]
        build_clib.spawn(command)

        shutil.move(d_file, tmp_file)

        command = [
            "sed -e 's|.*:|{0}: {1}|' < {2} > {1}".format(
                o_file,
                d_file,
                tmp_file
            )
        ]
        build_clib.spawn(command)

        command = [
            "sed -e 's/.*://' -e 's/\\$//' < {0} | fmt -1 | "
            "sed -e 's/^ *//' -e 's/$/:/' >> {1}".format(tmp_file, d_file)
        ]
        build_clib.spawn(command)

        os.remove(tmp_file)

        command = [self.cc] + self.c_flags + self.t_arch + self.include_dirs
        command += ['-o', o_file, c_file]
        build_clib.spawn(command, cwd=build_clib.build_temp)

        return o_file

    def _compile_cpp(self, cpp_file, build_clib):
        temp_path = os.path.join(build_clib.build_temp, self.name)

        with spawn_process.print_lock:
            sys.stdout.write(
                'compiling ' + os.path.split(cpp_file)[-1] + '...\n'
            )
            sys.stdout.flush()

        cpp_file = os.path.abspath(cpp_file)
        file_name = os.path.splitext(os.path.split(cpp_file)[-1])[0]
        d_file = os.path.join(temp_path, file_name + '.d')
        tmp_file = d_file + '.tmp'
        o_file = os.path.join(temp_path, file_name + '.o')

        command = [self.cxx] + self.c_flags + self.cpp_flags
        command += self.include_dirs + [cpp_file, '>', d_file]
        build_clib.spawn(command)

        shutil.move(d_file, tmp_file)

        command = [
            "sed -e 's|.*:|{0}: {1}|"
            "' < {2} > {1}".format(o_file, d_file, tmp_file)
        ]
        build_clib.spawn(command)

        command = [
            "sed -e's/.*://' -e 's/\\$//' < {0} | fmt -1 | sed -e "
            "'s/^ *//' -e 's/$/:/' >> {1}".format(tmp_file, d_file)
        ]
        build_clib.spawn(command)

        os.remove(tmp_file)

        command = [self.cxx] + self.c_flags + self.cpp_flags + self.t_arch
        command += self.include_dirs + ['-o', o_file, cpp_file]
        build_clib.spawn(command, cwd=build_clib.build_temp)

        return o_file

    def build(self, _):
        raise NotImplementedError

    def _build(self, build_clib):
        temp_path = build_clib.build_temp
        build_path = build_clib.build_clib

        build_path = os.path.join(build_path, self.name)
        temp_path = os.path.join(temp_path, self.name)

        if not os.path.exists(build_path):
            distutils.log.debug('Creating directory ' + build_path)
            os.makedirs(build_path)

        if not os.path.exists(temp_path):
            distutils.log.debug('Creating directory ' + temp_path)
            os.mkdir(temp_path)

        objects = []
        thread_event = threading.Event()

        def do(files):
            objs = []
            while files:
                f = files.pop(0)
                check_f = os.path.join(
                    temp_path,
                    os.path.split(f)[-1]
                )

                check_f = os.path.splitext(check_f)[0]

                for ext in ('.o', '.obj'):
                    if os.path.exists(check_f + ext):
                        obj = check_f + ext
                        break
                else:
                    if not files:
                        evt = self._running_threads[threading.current_thread()]
                        evt.set()

                    if f.endswith('cpp'):
                        obj = self._compile_cpp(f, build_clib)
                    else:
                        obj = self._compile_c(f, build_clib)

                objs.append(obj)

            objects.extend(objs)

            threads.remove(threading.current_thread())

            if not threads:
                thread_event.set()

        sources = self.sources[:]

        split_files = []
        num_files = int(round(len(sources) / 20))

        while sources:
            try:
                split_files += [sources[:num_files]]
                sources = sources[num_files:]
            except IndexError:
                split_files += [sources[:]]
                del sources[:]

        threads = []

        for fls in split_files:

            while len(threads) >= 12:
                thread_event.wait(0.1)

            t = threading.Thread(target=do, args=(fls,))
            t.daemon = True
            self._running_threads[t] = threading.Event()
            threads += [t]
            t.start()

        thread_event.wait()

        self.link(objects, build_clib)
