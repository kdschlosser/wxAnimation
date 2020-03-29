# -*- coding: utf-8 -*-

from __future__ import print_function
import sys
import os
from distutils.spawn import find_executable


def check_packages():
    pkg_config = find_executable("pkg-config")
    print("Found pkg-config : {0}".format(pkg_config))

    if pkg_config:
        from . import pkgconfig

        packages = ['']

        for package in pkgconfig.list_all():
            if len(packages[-1] + package + ', ') > 78:
                packages += ['']

            packages[len(packages) - 1] += package + ', '

        packages = '\n'.join('  ' + pkg for pkg in packages)[:-2]

        print('Installed packages:')
        print(packages)


def setup():
    if sys.platform.startswith('win'):
        from . import msvc
        print(msvc.environment)

        os.environ['LD'] = 'lib.exe'
        os.environ['AR'] = 'link.exe'
        os.environ['CXX'] = 'cl.exe'
        os.environ['CC'] = 'cl.exe'
        os.environ['RANLIB'] = ''

    elif sys.platform.startswith("cygwin"):
        gcc = find_executable("gcc")
        gpp = find_executable("g++")
        ar = find_executable('ar')
        ld = find_executable('ld')
        ranlib = find_executable('ranlib')
        cc = os.environ.get('CC', '')
        cxx = os.environ.get('CXX', '')
        ar_env = os.environ.get('AR', '')
        ld_env = os.environ.get('LD', '')
        ranlib_env = os.environ.get('RANLIB', '')

        if ld:
            if ld != ld_env and ar_env.endswith('ld'):
                ld = ld_env
            else:
                os.environ['LD'] = ld
        elif ld_env.endswith('ld'):
            ld = ld_env
        else:
            raise RuntimeError('Unable to locate ld')

        if ranlib:
            if ranlib != ranlib_env and ranlib_env.endswith('ranlib'):
                ranlib = ranlib_env
            else:
                os.environ['RANLIB'] = ranlib
        elif ranlib_env.endswith('ranlib'):
            ranlib = ranlib_env
        else:
            raise RuntimeError('Unable to locate ranlib')

        if ar:
            if ar != ar_env and ar_env.endswith('ar'):
                ar = ar_env
            else:
                os.environ['AR'] = ar
        elif ar_env.endswith('ar'):
            ar = ar_env
        else:
            raise RuntimeError('Unable to locate ar')

        if gcc:
            if gcc != cc and cc.endswith('gcc'):
                gcc = cc
            else:
                os.environ['CC'] = gcc
        elif cc.endswith('gcc'):
            gcc = cc
        else:
            raise RuntimeError('Unable to locate gcc')

        print("Found gcc : {0}".format(gcc))

        if gpp:
            if gpp != cxx and cxx.endswith('g++'):
                gpp = cxx
            else:
                os.environ['CXX'] = gpp
        elif cxx.endswith('g++'):
            gpp = cxx
        else:
            raise RuntimeError('Unable to locate g++')

        print("Found g++ : {0}".format(gpp))
        print("Found ar : {0}".format(ar))
        print("Found ld : {0}".format(ld))
        print("Found ranlib : {0}".format(ranlib))
        check_packages()

    elif sys.platform.startswith("darwin"):
        clang = find_executable("clang")
        clang_pp = find_executable("clang++")
        ar = find_executable('ar')
        ld = find_executable('ld')
        ranlib = find_executable('ranlib')

        cc = os.environ.get('CC', '')
        cxx = os.environ.get('CXX', '')
        ar_env = os.environ.get('AR', '')
        ld_env = os.environ.get('LD', '')
        ranlib_env = os.environ.get('RANLIB', '')

        if ranlib:
            ranlib = 'ranlib'
            if ranlib != ranlib_env and ranlib_env.endswith('ranlib'):
                ranlib = ranlib_env
            else:
                os.environ['RANLIB'] = 'ranlib'
        elif ranlib_env.endswith('ranlib'):
            ranlib = ranlib_env
        else:
            raise RuntimeError('Unable to locate ranlib')

        if ar:
            if ar != ar_env and ar_env.endswith('ar'):
                ar = ar_env
            else:
                os.environ['AR'] = 'ar'
        elif ar_env.endswith('ar'):
            ar = ar_env
        else:
            raise RuntimeError('Unable to locate ar')

        if clang:
            if clang != cc and cc.endswith('clang'):
                clang = cc
            else:
                os.environ['CC'] = clang
        elif cc.endswith('clang'):
            clang = cc
        else:
            raise RuntimeError('Unable to locate clang')

        print("Found clang : {0}".format(clang))

        if clang_pp:
            if clang_pp != cxx and cxx.endswith('clang++'):
                clang_pp = cxx
            else:
                os.environ['CXX'] = clang_pp
        elif cxx.endswith('clang++'):
            clang_pp = cxx
        else:
            raise RuntimeError('Unable to locate clang++')

        if ld:
            if ld != ld_env and ar_env.endswith('ld'):
                ld = ld_env
            else:
                os.environ['LD'] = 'ld'
        elif ld_env.endswith('ld'):
            ld = ld_env
        else:
            ld = 'ld'
            os.environ['LD'] = 'ld'

        print("Found clang : {0}".format(clang))
        print("Found clang++ : {0}".format(clang_pp))
        print("Found ar : {0}".format(ar))
        print("Found ld : {0}".format(ld))
        print("Found ranlib : {0}".format(ranlib))

        check_packages()

    elif sys.platform.startswith('freebsd'):
        c = find_executable("cc")
        cpp = find_executable("c++")
        gmake = find_executable("gmake")
        cc = os.environ.get('CC', '')
        cxx = os.environ.get('CXX', '')

        if not gmake:
            raise RuntimeError('Unable to locate gmake')

        if c:
            if c != cc and cc.endswith('cc'):
                c = cc
            else:
                os.environ['CC'] = c
        elif cc.endswith('cc'):
            c = cc
        else:
            raise RuntimeError('Unable to locate cc')

        print("Found cc : {0}".format(c))

        if cpp:
            if cpp != cxx and cxx.endswith('c++'):
                cpp = cxx
            else:
                os.environ['CXX'] = cpp
        elif cxx.endswith('c++'):
            cpp = cxx
        else:
            raise RuntimeError('Unable to locate c++')

        print("Found c++ : {0}".format(cpp))
        print("Found gmake : {0}".format(gmake))
        check_packages()

        os.environ['LD'] = cpp
        os.environ['AR'] = 'ar'
        os.environ['RANLIB'] = 'ranlib'

    elif sys.platform.startswith('sunos'):
        gcc = find_executable("gcc")
        gpp = find_executable("g++")
        make = find_executable("make")
        cc = os.environ.get('CC', '')
        cxx = os.environ.get('CXX', '')

        if not make:
            raise RuntimeError('Unable to locate make')

        if gcc:
            if gcc != cc and cc.endswith('gcc'):
                gcc = cc
            else:
                os.environ['CC'] = gcc
        elif cc.endswith('gcc'):
            gcc = cc
        else:
            raise RuntimeError('Unable to locate gcc')

        print("Found gcc : {0}".format(gcc))

        if gpp:
            if gpp != cxx and cxx.endswith('g++'):
                gpp = cxx
            else:
                os.environ['CXX'] = gpp
        elif cxx.endswith('g++'):
            gpp = cxx
        else:
            raise RuntimeError('Unable to locate g++')

        print("Found g++ : {0}".format(gpp))
        print("Found make : {0}".format(make))
        check_packages()

        os.environ['LD'] = gpp
        os.environ['AR'] = 'ar'
        os.environ['RANLIB'] = 'ranlib'

    elif sys.platform.startswith('linux'):
        gcc = find_executable("gcc")
        gpp = find_executable("g++")
        ar = find_executable('ar')
        ld = find_executable('ld')
        ranlib = find_executable('ranlib')
        cc = os.environ.get('CC', '')
        cxx = os.environ.get('CXX', '')
        ar_env = os.environ.get('AR', '')
        ld_env = os.environ.get('LD', '')
        ranlib_env = os.environ.get('RANLIB', '')

        if ranlib:
            ranlib = 'ranlib'
            if ranlib != ranlib_env and ranlib_env.endswith('ranlib'):
                ranlib = ranlib_env
            else:
                os.environ['RANLIB'] = 'ranlib'
        elif ranlib_env.endswith('ranlib'):
            ranlib = ranlib_env
        else:
            raise RuntimeError('Unable to locate ranlib')

        if ar:
            if ar != ar_env and ar_env.endswith('ar'):
                ar = ar_env
            else:
                os.environ['AR'] = 'ar'
        elif ar_env.endswith('ar'):
            ar = ar_env
        else:
            raise RuntimeError('Unable to locate ar')

        if gcc:
            if gcc != cc and cc.endswith('gcc'):
                gcc = cc
            else:
                os.environ['CC'] = 'gcc'
        elif cc.endswith('gcc'):
            gcc = cc
        else:
            raise RuntimeError('Unable to locate gcc')

        print("Found gcc : {0}".format(gcc))

        if gpp:
            if gpp != cxx and cxx.endswith('g++'):
                gpp = cxx
            else:
                os.environ['CXX'] = 'g++'
        elif cxx.endswith('g++'):
            gpp = cxx
        else:
            raise RuntimeError('Unable to locate g++')

        if ld:
            if ld != ld_env and ar_env.endswith('ld'):
                ld = ld_env
            else:
                os.environ['LD'] = 'ld'
        elif ld_env.endswith('ld'):
            ld = ld_env
        else:
            ld = gpp
            os.environ['LD'] = 'g++'

        print("Found gcc : {0}".format(gcc))
        print("Found g++ : {0}".format(gpp))
        print("Found ar : {0}".format(ar))
        print("Found ld : {0}".format(ld))
        print("Found ranlib : {0}".format(ranlib))

        check_packages()

    else:
        raise RuntimeError(
            "No Library available for platform {0}".format(sys.platform)
        )
