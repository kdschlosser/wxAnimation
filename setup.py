
from setuptools import setup, find_packages


from build_framework.extensions import Extension


setup(
    name='wxAnimation',
    version='0.0.1a',
    url='https://github.com/kdschlosser/wxAnimation',
    packages=find_packages(include=['webp', 'webp.*', 'webp_build']),
    package_data={'webp_build': ['*.h', '*.c']},
    author='Kevin Schlosser',
    description='wxPython animation decoders',
    license='MIT',
    setup_requires=['cffi>=1.0.3'],
    cffi_modules=['flif_builder/builder.py:ffibuilder', 'webp_builder/builder.py:ffibuilder'],
    install_requires=['wxPython>=4.0.0'],
)